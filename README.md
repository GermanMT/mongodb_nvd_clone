# A MongoDB clone from NVD database

## National Vulnerability Database (NVD)

The NVD is the U.S. government repository of standards based vulnerability management data represented using the Security Content Automation Protocol (SCAP). This data enables automation of vulnerability management, security measurement, and compliance. The NVD includes databases of security checklist references, security-related software flaws, misconfigurations, product names, and impact metrics.

## Why is this tool necessary?

Currently the only way to consume NVD data is through a public [API](https://nvd.nist.gov/general/news/api-20-announcements) that has [limitations](https://nvd.nist.gov/general/news/API-Key-Announcement) when it comes to consuming it. So they recommend using this [workflow](https://nvd.nist.gov/developers/api-workflows), which in a nutshell explains that you should clone all the NVD data using API calls, extracting as much information as possible. Later on, keep your clone up to date with calls to the latest updated data, recommending that these calls be made at most once every two hours.

## How does it work?

This repository solves this problem by creating an automatic clone on a MongoDB database that the developer has already initialised. This command also create an index for the own id extracted from NVD (cve:id, cpe_match:matchCriteriaId and cpe:cpeNameId). This is done using the command:

```
python3 main.py clone [your_mongodb_uri] --nvd_api [your_nvd_api_key]
```

You can also create a cron job that is triggered every two hours, which keeps your local database in sync with the NVD database. I recommend using it right after using the clone command. Using this command:

```
python3 main.py sync [your_mongodb_uri] --nvd_api [your_nvd_api_key]
```

This commands requires the uri of the initialised MongoDB database and an optional NVD API [key](https://nvd.nist.gov/developers/request-an-api-key). Although the API key is optional, using it will make the cloning and sync process go 5 to 6 times faster.
