import json
import logging
import os
from datetime import datetime
import Levenshtein
import httpx
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein

file_path = "world_universities_and_domains.json"


def download():
    response = httpx.get(
        "https://raw.githubusercontent.com/Hipo/university-domains-list/master/"
        "world_universities_and_domains.json",
        timeout=3
    )
    with open(file_path, 'w') as f:
        json.dump(response.json(), f)


class SearchUniversity:
    def __init__(self):
        if not os.path.exists(file_path):
            download()
        modified_time = os.path.getmtime(file_path)
        modified_days_ago = (datetime.now() - datetime.fromtimestamp(modified_time)).days
        if modified_days_ago > 30:  # file downloaded >30 days ago
            download()
        try:
            with open(file_path, 'r') as g:
                universities_list = json.load(g)
        except json.JSONDecodeError:
            download()
            try:
                with open(file_path, 'r') as g:
                    universities_list = json.load(g)
            except json.JSONDecodeError:
                logging.warning("Cannot recognize the format of universities list from "
                                f"github.com/Hipo/university-domains-list, so cannot "
                                f"generate the country where universities locate.")
                universities_list = {"web_pages": [], "name": "", "alpha_two_code": "",
                        "state-province": "", "domains": [], "country": ""}
        self.university_list = universities_list
        self.names = [u.get("name", "") for u in universities_list]

    def search_university(self, search_string):
        """
        Searches for the most likely university based on the provided name.
        """
        result = process.extractOne(
            query=search_string,
            choices=self.names,
            scorer=Levenshtein.distance,
            score_cutoff=50
        )
        return self.university_list[result[2]]
