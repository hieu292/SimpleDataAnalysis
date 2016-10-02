import codecs
from datetime import datetime,date
from loading import printProgress
import re

def loadData(name):
    content = codecs.open(name, 'r', 'utf8').read()
    splitContent = content.split('\r\n')
    return splitContent

def transformData(splitContent):
    data = []
    headContent = splitContent[0]
    bodyContent = splitContent[1:]
    print("Length of records: ", len(bodyContent))
    i = 0
    print("Transforming data:")
    # Initial call to print 0% progress
    printProgress(i, len(bodyContent), prefix='Progress:', suffix='Complete', barLength=50)
    for row in bodyContent:
        col = row.split(',')
        col[0] = datetime.strptime(col[0], '%m/%d/%Y %H:%M')
        col[3] = convertStr(col[3])
        data.append(col)
        # Update Progress Bar
        i += 1
        printProgress(i, len(bodyContent), prefix='Progress:', suffix='Complete', barLength=50)
    return data,headContent



def convertStr(utf8_str):
    INTAB = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ"
    INTAB = [ch.encode('utf8') for ch in INTAB]
    OUTTAB = "a" * 17 + "o" * 17 + "e" * 11 + "u" * 11 + "i" * 5 + "y" * 5 + "d"
    replaces_dict = dict(zip(INTAB, OUTTAB))
    for key, value in replaces_dict.items():
        utf8_str = utf8_str.replace(key.decode('utf8'), value)
    utf8_str = utf8_str.replace(' ', '')
    utf8_str = utf8_str.lower()
    return utf8_str
def getResult(data, queries):
    for record in data:
        checkRecord = False
        checkRecordCount = 0
        for index,que in enumerate(queries):
            query = que["query"]
            if query["Date Recruited"] is not None:
                conditions = query["Date Recruited"].split("|")
                for condition in conditions:
                    if condition == "weekend":
                        if record[0].weekday() == (5 or 6):
                            checkRecord = True
                        else:
                            checkRecordCount += 1
                    if re.match('\d+(PM|AM)-\d+(PM|AM)', condition):
                        m = re.match('(\d+)(PM|AM)-(\d+)(PM|AM)', condition)
                        startTime = int(m.group(1)) if(m.group(1) == "AM") else (int(m.group(1)) + 12)
                        endTime = int(m.group(3)) if(m.group(4) == "AM") else (int(m.group(3)) + 12)
                        hourOfRecord = record[0].hour
                        if startTime <= hourOfRecord <= endTime:
                            checkRecord = True
                        else:
                            checkRecordCount += 1
            if query["Gender"] is not None:
                if query["Gender"] == record[1]:
                    checkRecord = True
                else:
                    checkRecordCount += 1
            if query["Age"] is not None:
                conditions = query["Age"].split("|")
                ageOfRecord = int(record[2]) if re.match('\d.',record[2]) else 0
                if re.match("\d.", conditions[0]):
                    #match #age
                    ageOfCondition = int(conditions[0])
                    if conditions[1] == "old":
                        if ageOfRecord > ageOfCondition:
                            checkRecord = True
                        else:
                            checkRecordCount += 1
                    if conditions[1] == "young":
                        if ageOfCondition > ageOfRecord:
                            checkRecord = True
                        else:
                            checkRecordCount += 1
                    if conditions[1] == "equal":
                        if ageOfRecord == ageOfCondition:
                            checkRecord = True
                        else:
                            checkRecordCount += 1

                if re.match("\w{3} \d., \d{4}", conditions[0]):
                    # match date of birth "mmm dd, yyyy"
                    today = date.today()
                    born = datetime.strptime(conditions[0], "%b %d, %Y")
                    ageOfCondition = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                    if conditions[1] == "old":
                        if ageOfRecord > ageOfCondition:
                            checkRecord = True
                        else:
                            checkRecordCount += 1
                    if conditions[1] == "young":
                        if ageOfCondition > ageOfRecord:
                            checkRecord = True
                        else:
                            checkRecordCount += 1
                    if conditions[1] == "equal":
                        if ageOfRecord == ageOfCondition:
                            checkRecord = True
                        else:
                            checkRecordCount += 1
            if query["Province"] is not None:
                conditions = query["Province"].split("|")
                countError = 0
                for condition in conditions:
                    if condition == record[3]:
                        checkRecord = True
                    else:
                        countError += 1
                if countError == len(conditions):
                    checkRecordCount += 1
            if query["Country"] is not None:
                conditions = query["Country"].split("|")
                countError = 0
                for condition in conditions:
                    if condition == record[4]:
                        checkRecord = True
                    else:
                        countError += 1
                if countError == len(conditions):
                    checkRecordCount += 1
            if checkRecord and checkRecordCount == 0:
                queries[index]["result"]["TotalCount"] += 1
                queries[index]["result"]["List"].append(record)
            else:
                checkRecordCount = 0
    return queries

if __name__ == "__main__":
    fileContent = loadData('sample-data-test.csv')
data, header = transformData(fileContent)
queries = [
    {
        "name": "query-1",
        "query": {"Date Recruited": None, "Gender": None, "Age": "May 14, 1984|old", "Province": None, "Country": None},
        "result": {"TotalCount": 0, "List": []}
    },
    {
        "name": "query-2",
        "query": {"Date Recruited": None, "Gender": None, "Age": None, "Province": "hcm|hcmcity|hochiminh|hochiminhcity|tphcm|tphcmcity|tphochiminh|tphochiminhcity|tp.hcm|saigon", "Country": None},
        "result": {"TotalCount": 0, "List": []}
    },
    {
        "name": "query-3",
        "query": {"Date Recruited": None, "Gender": None, "Age": "20|young", "Province": "hcm|hcmcity|hochiminh|hochiminhcity|tphcm|tphcmcity|tphochiminh|tphochiminhcity|tp.hcm|saigon", "Country": None},
        "result": {"TotalCount": 0, "List": []}
    },
    {
        "name": "query-4",
        "query": {"Date Recruited": "weekend|6PM-10PM", "Gender": None, "Age": None, "Province": "hcm|hcmcity|hochiminh|hochiminhcity|tphcm|tphcmcity|tphochiminh|tphochiminhcity|tp.hcm|saigon|hanoi", "Country": None},
        "result": {"TotalCount": 0, "List": []}
    }
]
# print(data)
result = getResult(data, queries)
print(result[0]["name"])
print(result[0]["result"]["TotalCount"], "results")
print(result[1]["name"])
print(result[1]["result"]["TotalCount"], "results")
print(result[2]["name"])
print(result[2]["result"]["TotalCount"], "results")
print(result[2]["result"]["List"])
print(result[3]["name"])
print(result[3]["result"]["TotalCount"], "results")
print(result[3]["result"]["List"])