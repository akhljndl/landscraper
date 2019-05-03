#!/usr/bin/env python
# coding: utf-8

# ./scraper.py

from bs4 import BeautifulSoup
import requests
import os
import csv
import pandas as pd
import re
from glob import glob


class Patent:

    def __init__(self, title, number, assignee, pub_date, source):
        """Defining pertinent attributes
        """
        self.title = title
        self.number = number
        self.assignee = assignee
        self.pub_date = pub_date
        self.source = source

    def soupify(self):
        """Soupify for BeautifulSoup
        """
        src = requests.get('{}'.format(self.source)).text
        soup = BeautifulSoup(src, 'lxml')
        return soup

    def description(self, soup):
        """Returns a detailed description of target patent application
        Can include Abstract, Summary and Background
        """
        description = soup.find('div', class_='description').text
        return description

    def genContent(self, classification, corpus_dir, soup):
        """Generates a training document for a corpus
        """
        class_dir = os.path.join(corpus_dir, classification)
        file_name = re.sub('[^A-Za-z0-9]+', '', self.number)

        if os.path.isdir(class_dir):
            write_path = os.path.join(class_dir, file_name)

            try:
                self.writeContent(write_path)

            except:
                print("Failed to generate {}".format(self.number))

        else:
            os.mkdir(class_dir)
            write_path = os.path.join(class_dir, file_name)

            try:
                self.writeContent(write_path)

            except:
                print("Failed to generate {}".format(self.number))

    def writeContent(self, write_file):
        """Writes the content for a training document
        """
        with open(write_file, "w") as wf:
            header = str(self.title) + "\n" + str(self.number) + "\n" + str(self.assignee) + \
                "\n" + str(self.pub_date) + "\n" + str(self.source) + "\n"
            wf.write(header)
            try:
                desc = self.description(soup).encode('utf-8').strip()
                wf.write(desc)
            except:
                print("Encoding messed up for {}".format(write_file))
        wf.close()

        def cleanCSV(csv_file):
    """The .csv file downloadable from patents.google.com.
    However, for our purposes, the downloaded .csv has more information than we need.
    We keep pertient columns, and delete rows that are associated with non-US patents.
    """

    df = pd.read_csv(csv_file, error_bad_lines=False, sep=',')
    df = df.drop(["inventor/author", "priority date", "filing/creation date",
                  "grant date", "representative figure link"], axis=1)
    df = df[df["id"].str.contains("US")]
    return df


def definePatent(dataframe):
    """Uses Patent class to generate patents for further processing
    """
    patents = []
    for index, row in dataframe.iterrows():
        patent = Patent(row["title"], row["id"], row["assignee"],
                        row["publication date"], row["result link"])
        patents.append(patent)
    return patents


def classify(csv_file):
    classification = os.path.basename(csv_file).split(".")[0]
    return classification
