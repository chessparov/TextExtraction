import numpy as np
import pandas as pd
from pypdf import PdfReader


def getTable(page_text: str, begin_word: str, end_word: str) -> str:
    """
    This function takes the whole page as a long string and isolates
    only the worthy data. You have to manually check, by simply printing the whole page, which
    words are the boundaries of the data you're looking for.
    :param end_word: First word of the non-relevant section, following the relevant section
    :param begin_word: First word of the relevant section
    :param page_text: Raw text
    :return: A string containing the processed text
    """

    if begin_word in page_text and end_word in page_text:
        beginning_index = page_text.find(begin_word)
        ending_index = page_text.find(end_word)
        page_text = page_text[beginning_index:ending_index]
        return page_text
    else:
        return "Target not found!"


def transformData(text: str,
                  rows: int,
                  cols: int,
                  where_to_insert: int | None = None,
                  what_to_insert: list | None = None) -> pd.DataFrame:
    """
    Pass the already isolated text containing only the values. Process it in order to separate correctly
    the values and save it in tabular form in a pandas dataframe.
    :param what_to_insert: In case of missing values, add them manually
    :param where_to_insert: Index of where to insert the missing values
    :param cols: Number of cols of the dataframe
    :param rows: Number of rows of the Dataframe
    :param text: Actual text to process
    :return: A pandas dataframe containing the tabular data of the values
    """

    # First cycle for separating values
    temp_list = []
    for value1 in text.split():
        temp_list.append(value1)

    # Not all values successfully separated, you can convince yourself by putting a print(temp_list) there.
    # To separate them correctly, we create a list with the glued values, and two list where we put them once separated.
    lstValues_to_remove = []
    lstFirstParts = []
    lstSecondParts = []

    # We avoid to cycle to far. I came up with this solution simpy by looking at the data and trying out things.
    # For sure there are better and cleaner ways to do this.
    max_i = len(temp_list)
    for i, value2 in enumerate(temp_list):
        # I realized that glued values are never at the end or in the beginning
        if i != 0 and i != max_i - 1:
            # Glued values are never dotted, but are typically surrounded by dotted data.
            if "." not in value2 and "." in temp_list[i - 1] and "." in temp_list[i + 1]:
                # Here we simply split the glued values
                split_length = int(len(value2)/2)
                first_part = value2[:split_length]
                second_part = value2[split_length:]

                # Here we add the results to the lists
                lstValues_to_remove.append(value2)
                lstFirstParts.append(first_part)
                lstSecondParts.append(second_part)

    # We now substitute the correct values
    for i, item in enumerate(lstValues_to_remove):
        ind = temp_list.index(item)
        temp_list[ind] = lstFirstParts[i]
        temp_list.insert(ind, lstSecondParts[i])

    # Insert missing values if present
    if what_to_insert is not None:
        for element in what_to_insert:
            temp_list.insert(where_to_insert, element)

    # Convert to a numpy array to use the reshape method
    temp_list = np.array(temp_list)

    # You can directly write the data like that, but we prefer to use the pandas dataframe
    # with open("data.txt", "r+") as dataFile:
    #     for item in temp_list:
    #         dataFile.write(item + "\n")

    # Let's reshape the array like originally in the pdf
    matrix = temp_list.reshape(rows, cols)

    # Header for the dataframe, useful for visual inspections
    # you can later save the data without the header
    header = ["°C", "-10", "-9", "-8", "-7", "-6", "-5", "-4", "-3", "-2", "-1", "0", "°C"]
    return pd.DataFrame(matrix, columns=header)


# Load document and transform it to text
convert_to_text = PdfReader("thermocouple-type-k-celsius.pdf")

# Uncomment and cycle through all pages and with a simple print of all the text, take a look at the boundary words
# for page in convert_to_text.pages:
#     print(page.extract_text())

# Extract only first page
first_page = convert_to_text.pages[0]
first_page_text = first_page.extract_text()

# Process the text
first_table = getTable(first_page_text, "-260", "MAXIMUM")

# Those values are manually counted for simplicity, but it doesn't take much time
# as the values are already in groups of 5
first_page_cols = 13
first_page_rows = 107
dtfFirstTable = transformData(first_table, first_page_rows, first_page_cols)

# Save the data in whatever file. Pandas offer different options. If there's not the desired option
# you can always use the syntax at line 78
dtfFirstTable.to_excel("typeK_page1.xlsx")

# Let's proceed to the second page
second_page = convert_to_text.pages[1]
second_page_text = second_page.extract_text()

second_page_table = getTable(second_page_text, "800", "TYPE")

second_page_cols = 13
second_page_rows = 58

# Added additional arguments in order to complete correctly the dataframe. How did I came up with this?
# I simply made it run without the arguments, got the error "cannot reshape array of size 746 in size (58, 13)",
# so I took a look at the pdf and saw the table had some missing values, so I added those arguments and added the blank
# elements in the 745° position
dtfSecondTable = transformData(second_page_table,
                               second_page_rows,
                               second_page_cols,
                               745,
                               ["", "", "", "", "", "", "", ""]
                               )
dtfSecondTable.to_excel("typeK_page2.xlsx")

# Now if we want we can glue together the tables and export them in different ways
dtfTypeK = pd.concat([dtfFirstTable, dtfSecondTable])
dtfTypeK.to_excel("typeK.xlsx")
