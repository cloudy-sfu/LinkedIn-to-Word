import json
import os
from argparse import ArgumentParser

from docx.opc.exceptions import PackageNotFoundError
from docxtpl import DocxTemplate
from linkdapi import LinkdAPI

from universities import SearchUniversity
from websites import convert_url
from jinja2 import Environment

# %% Get arguments.
parser = ArgumentParser()
parser.add_argument("--linkdapi_key", required=True)
parser.add_argument("--profile_id", required=True)
parser.add_argument("--template", default="resume.docx")
cmd, _ = parser.parse_known_args()

# %% Initialization.
os.makedirs("profiles", exist_ok=True)
client = LinkdAPI(api_key=cmd.linkdapi_key)

# %% Get profile.
profile = client.get_full_profile(username=cmd.profile_id)['data']

# %% Pre-processing.
# Add school's country
search_engine = SearchUniversity()
for education in profile['educations']:
    school_info = search_engine.search_university(education['schoolName'])
    education['country'] = school_info.get("country", "")
# Aggregate roles of the same company
companies = {}
for position in profile['fullPositions']:
    employer = {}
    role = {}
    for k, v in position.items():
        if k.startswith("company"):
            employer[k] = v
        else:
            role[k] = v
    company_id = position["companyId"]
    employer['country'] = position['location'].split(',')[-1].strip()
    if company_id in companies.keys():
        companies[company_id]['roles'].append(role)
    else:
        companies[company_id] = employer
        companies[company_id]['roles'] = [role]
profile['fullPositions'] = companies

# %% Add contact information.
contact_info = client.get_contact_info(cmd.profile_id)['data']
profile.update(contact_info)
with open(os.path.join("profiles", cmd.profile_id + ".json"), "w") as f:
    json.dump(profile, f)

# %% Customized rendering function.
# Bullet point: https://github.com/elapouya/python-docx-template/issues/73
def get_key_points(desc_):
    key_points = []
    for item_text in desc_.split("\n"):
        if len(item_text) == 0:
            continue
        if item_text[0] in ("*", "•", "-", "+"):
            is_bullet = True
            item_text = item_text[1:].strip()
        else:
            is_bullet = False
        key_points.append({"bullet": is_bullet, "text": item_text})
    return key_points


def concat_date(date_):
    date_str = ''
    if date_['year'] > 0:
        date_str += str(date_['year']).zfill(4)
    if date_['month'] > 0:
        date_str += '-' + str(date_['month']).zfill(2)
    if date_['day'] > 0:
        date_str += '-' + str(date_['day']).zfill(2)
    return date_str


env = Environment()
env.filters['get_key_points'] = get_key_points
env.filters['concat_date'] = concat_date
env.filters['convert_url'] = convert_url

# %% Render.
resume = DocxTemplate(os.path.join("templates", cmd.template))
# If template is not valid: PackageNotFoundError
try:
    resume.render(profile, jinja_env=env)
except PackageNotFoundError:
    raise Exception("The resume template is invalid.")
for paragraph in resume.paragraphs:  # remove empty paragraphs
    if len(paragraph.text) == 0:
        p = paragraph._element
        p.getparent().remove(p)
        p._p = p._element = None
resume.save(os.path.join("profiles", cmd.profile_id + ".docx"))
