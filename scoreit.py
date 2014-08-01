"""
Copyright (c) 2014 Jeremy Rubin http://rubin.io

An algorithm/Library for reducing multiple judge scores into meaningful rankings for hackathons or contests.

Here is a sample schema for the judging data in CSV:

competitor, judge, score1, score2... scoreN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""
import csv

def groupBy(key, l):
    """ Take in a list of maps and a key and group it into a map from key to list of maps"""
    result = {item[key]:[] for item in l}
    for item in l:
        result[item[key]].append(item)
    return result
def mapTypes(fields, typeConv,l):
    """ Take in a set of fields, a type casting function, and a list of maps and convert each field in each map to the proper type"""
    return map(lambda x: {key:(typeConv(value) if key in fields else value) for key, value in x.iteritems()},l)
def norm(std,avg, x):
    """ normalize a value x from a distribution defined by a std and avg"""
    return 0 if std == 0 else (x-avg)/std
def stddev(group, avg=None):
    """ compute the stddev of a group, optionally passing in the avg """
    if not avg:
        avg = sum(group)/float(len(group))
    return (sum(map(lambda x: (x-avg)**2, group))/len(group))**.5
def normalize(fields, groups):
    """ Normalize the fields individually in each group independently from other groups"""
    for groupName, group in groups.iteritems():
        n = len(group)
        avgs = {field:sum(member[field] for member in group)/n for field in fields}
        stds = {field:stddev(map(lambda x: x[field], group), avgs[field]) for field in fields}
        for member in group:
            for field in fields:
                member[field] = norm(stds[field], avgs[field], member[field])
def weightedSum(fields, groups, saveTo):
    """ Sum the fields in each member of the group and save it to saveTo
        @fields is a map from field key to weight
    """
    for groupName, group in groups.iteritems():
        for member in group:
            member[saveTo] = sum(member[field]*weight for field, weight in fields.iteritems())
def computeScores(fileName, fields, judgesKey, projectKey, sumField, normalizeFields):
    """ Pass in a csv filepath, a list of fields to judge with, a judge identifier field, an entry identifier, a fresh field key, and a bool of
    weather or not to normalize all fields before summing and return a ranking of type [(score,project name)]"""
    with open(fileName, "r") as f:
        # Read in the entries
        rawEntries = list(csv.DictReader(f))
        # type-cast the proper fields
        entries = mapTypes(fields.keys(), float, rawEntries)
        # Group entries by judge name
        judgeGroup = groupBy(judgesKey, entries)
        # normalize the value of all fields individually
        if normalizeFields:
            normalize(fields.keys(), judgeGroup)
        # perform a weighted sum
        weightedSum(fields, judgeGroup, sumField)
        # normalize the sum field
        normalize([sumField], judgeGroup)
        # the entries grouping from before is still valid! regroup by project name
        projectGroup = groupBy(projectKey, entries)
        # calculate scores by averaging all of the entries for a given project
        scores = [(sum(score[sumField] for score in scoreSet)/float(len(scoreSet)),project) for project, scoreSet in projectGroup.iteritems()]
        return sorted(scores)[::-1]
"""
test case
if __name__ == "__main__":
    computeScores("asdf.csv", {"Progress":1,"Duplicate":1,"Design":1,"Quality of Video":1,"Miscellaneous":1}, "Judge", "Project Name", "sum", False)
"""
