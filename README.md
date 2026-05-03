# LinkedIn to Word
Generate resume in Microsoft Word format by information in LinkedIn profile

![](https://shields.io/badge/dependencies-Python_3.14-blue)
![](https://shields.io/badge/dependencies-linkdapi.com-blue)

## Acknowledgement

This program relies on commercial service of https://linkdapi.com/ Each resume costs 2 credits (0.02 USD, checked April 2026, first 100 credits free).

## Install

Visit https://linkdapi.com/ and register an account. Get API key.

Create and activate a Python virtual environment.

Run the following command in terminal.

```
pip install -r requirements.txt
```



## Usage

Run the following command with arguments.

```
python main.py
```

Arguments:

| Name             | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `--linkdapi_key` | API key of linkdapi, described in installation.              |
| `--profile_id`   | The string after https://www.linkedin.com/in/ in the URL of the profile to export. |
| `--template`     | Filename of customized template. The file should exist in `templates/` folder. |

The output resume is `profiles/${profile_id}.docx`.
