import DataPreprocessing_SA as dapr
import pathlib


dir_path = pathlib.Path.cwd()
sentimentdata_file_path = pathlib.Path(dir_path, "data", "doc_comment_summary.csv")
sentimentdata_file_pathxlsx = pathlib.Path(dir_path, "data", "doc_comment_summary.xlsx")
wordrating_file_path = pathlib.Path(dir_path, "data", "full_word_rating_after_coding.csv")




dp = dapr.DataPreprocessing_SA()
#dp.deleteTrain('testtrain.json') #удалить файл данных
#dp.writeTrain()
