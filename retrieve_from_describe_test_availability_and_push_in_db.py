from Test_downloading_datasets import test_dataset_availability_and_save_it
from extract_datasets_from_describe import collect_and_store_dataset_informations
from Add_data_in_database import append_data_in_db
from Set_environment_variables import set_env_var
from utils.general import get_data_directory_from_command_line
import copernicusmarine

def main():
    data_dir = get_data_directory_from_command_line()
    set_env_var()
    copernicusmarine.login()
    collect_and_store_dataset_informations(data_dir)
    test_dataset_availability_and_save_it(data_dir)
    append_data_in_db(data_dir)

if __name__ == "__main__":
    main()