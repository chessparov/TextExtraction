import numpy as np
import pandas as pd
from pypdf import PdfReader


def getTable(page_text: str, begin_word: str, end_word: str) -> str:
    """
    This function takes the whole page as a long string and isolates
    only the worthy data. You have to manually check, by simply printing the whole page, which
    words are the boundaries of the data you're looking for.
    :param end_word:
    :param begin_word:
    :param page_text:
    :return:
    """

    if begin_word in page_text and end_word in page_text:
        beginning_index = page_text.find(begin_word)
        ending_index = page_text.find(end_word)
        page_text = page_text[beginning_index:ending_index]
        return page_text
    else:
        return "Target not found!"


def transformData(text: str) -> pd.DataFrame:
    """
    Pass the already isolated text containing only the values. Process it in order to separate correctly
    the values and save it in tabular form in a pandas dataframe.
    :param text:
    :return:
    """

    # Those values are manually counted for simplicity, but it doesn't take much time
    # as the values are already in groups of 5
    values_per_row = 13
    rows = 107

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

    # Convert to a numpy array to use the reshape method
    temp_list = np.array(temp_list)

    # You can directly write the data like that, but we prefer to use the pandas dataframe
    # with open("data.txt", "r+") as dataFile:
    #     for item in temp_list:
    #         dataFile.write(item + "\n")

    # Let's reshape the array like originally in the pdf
    matrix = temp_list.reshape(rows, values_per_row)

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
table_text = getTable(first_page_text, "-260", "MAXIMUM")
dtfTable = transformData(table_text)

# Save the data in whatever file. Pandas offer different options. If there's not the
dtfTable.to_excel("typeK_page1.xlsx")
