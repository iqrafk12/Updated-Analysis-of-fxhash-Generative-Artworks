#!/usr/bin/python3
# Merged script: Collects data from fxhash, including random and latest generative tokens,
# performs static analysis, and logs errors and library details.

import requests
import json
import random
import datetime
import re
import csv
import os
from lxml import etree

# File name for CSV output
csv_filename = "fxhash_data.csv"

# Function to create the CSV file and write headers
def create_csv():
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Link Status", "Description", "Artwork Link", "IPFS Link", "p5.js Versions", "Other JS Libraries",
            "Artifact URI HTTP", "Artifact URI fxhash", "Display URI HTTP",
            "Display URI fxhash", "Thumbnail URI HTTP", "Thumbnail URI fxhash",
            "Generative URI HTTP", "Generative URI fxhash"
        ])

# Function to write data to CSV
def write_to_csv(data):
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

# GraphQL Query to get the latest generative tokens
def get_latest_generative_tokens():
    query = {
        "operationName": "GenerativeTokens",
        "variables": {
            "skip": 0,
            "take": 20,
            "sort": {"mintOpensAt": "DESC"},
            "filters": {"flag_in": ["CLEAN", "NONE"]}
        },
        "query": """
        query GenerativeTokens($skip: Int, $take: Int, $sort: GenerativeSortInput, $filters: GenerativeTokenFilter) {
          generativeTokens(skip: $skip, take: $take, sort: $sort, filters: $filters) {
            id
            name
            generativeUri
            slug
            flag
            author {
              name
            }
          }
        }
        """
    }

    response = requests.post("https://api.fxhash.xyz/graphql", json=query)

    # Handle potential errors in response
    try:
        return response.json()['data']['generativeTokens']
    except KeyError:
        print(f"Error fetching latest generative tokens: {response.status_code} - {response.text}")
        return []

# Function to get a random generative token
def get_random_token(maxtokenid):
    randomtoken = None
    for i in range(1, 10):
        randfxhash = random.randint(0, maxtokenid)
        r2 = requests.post("https://api.fxhash.xyz/graphql", json={
            "operationName": "GenerativeTokenFeatures",
            "variables": {"id": randfxhash},
            "query": """
            query GenerativeTokenFeatures($id: Float) {
              generativeToken(id: $id) {
                name
                generativeUri
                features
              }
            }
            """
        })
        if r2.json()['data']['generativeToken'] is not None:
            randomtoken = r2.json()['data']['generativeToken']
            randomtoken["id"] = randfxhash
            break
    return randomtoken

# Static analysis function to find scripts and libraries
def static_analysis(token):
    if "generativeUri" not in token:
        return {"status": "No URI found", "http_link": None}

    rooturl = token["generativeUri"].replace("ipfs://", "https://gateway.fxhash2.xyz/ipfs/")
    try:
        data = requests.get(rooturl)
        document = etree.HTML(data.text)
        scripts = document.xpath("//script[@src]/@src")

        scripts_info = []
        version_pattern = re.compile(r'v\d+(\.\d+)*')
        p5_version = None
        other_libraries = []

        for script in scripts:
            script_info = script
            if "p5" in script:
                # Example to fetch version of p5.js
                try:
                    script_content = requests.get(rooturl + "/" + script).text
                    p5_version = re.search(version_pattern, script_content)
                    if p5_version:
                        script_info += f" (p5.js version: {p5_version.group()})"
                except Exception:
                    script_info += " (p5.js version unknown)"
            else:
                other_libraries.append(script)

            scripts_info.append(script_info)

        return {
            "status": "Success",
            "http_link": rooturl,
            "p5_version": p5_version.group() if p5_version else "N/A",
            "other_libraries": ", ".join(other_libraries) if other_libraries else "None"
        }
    except requests.exceptions.RequestException as e:
        return {"status": "Error accessing IPFS content", "http_link": None}

# Function to describe the token for the CSV file
def describe_token(token):
    static_data = static_analysis(token)

    # Gather all the link formats
    artifact_uri_http = f"https://gateway.fxhash2.xyz/ipfs/{token['id']}/artifactUri"
    artifact_uri_fxhash = token["generativeUri"] + "/artifactUri"
    display_uri_http = f"https://gateway.fxhash2.xyz/ipfs/{token['id']}/displayUri"
    display_uri_fxhash = token["generativeUri"] + "/displayUri"
    thumbnail_uri_http = f"https://gateway.fxhash2.xyz/ipfs/{token['id']}/thumbnailUri"
    thumbnail_uri_fxhash = token["generativeUri"] + "/thumbnailUri"
    generative_uri_http = static_data["http_link"]
    generative_uri_fxhash = token["generativeUri"]
    
    # Construct the artwork link based on the token id
    artwork_link = f"https://www.fxhash.xyz/generative/{token['id']}"

    # Write all data to CSV
    write_to_csv([
        static_data["status"], token['name'], artwork_link, token["generativeUri"], static_data.get("p5_version", "N/A"),
        static_data.get("other_libraries", "None"), artifact_uri_http, artifact_uri_fxhash,
        display_uri_http, display_uri_fxhash, thumbnail_uri_http, thumbnail_uri_fxhash,
        generative_uri_http, generative_uri_fxhash
    ])

# Function to generate feed with both latest and random tokens
def generate_fxhash_feed():
    latest_tokens = get_latest_generative_tokens()
    if latest_tokens:
        maxtokenid = latest_tokens[0]['id']
        random_token = get_random_token(maxtokenid)

        # Describe both latest and random tokens
        if random_token:  # Check if a random token was found
            describe_token(random_token)
        for token in latest_tokens:
            describe_token(token)

# Main execution
if __name__ == "__main__":
    create_csv()  # Create CSV file and headers
    generate_fxhash_feed()
