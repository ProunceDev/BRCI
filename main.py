import os
from warnings import warn as raise_warning

from BRAPIF import *

# Note : every time you see unsigned_int() / signed_int() / bin_float(), byte_len * 8 is the number of bits.

# ------------------------------------------------------------
# DEFAULT VARIABLES AND SETUP
# ------------------------------------------------------------

# Setup variables
version : str = "C8"  # String

# Important variables
_cwd = os.path.dirname(os.path.realpath(__file__))  # File Path

# Temporary Variables
# No Temporary Variables.


# ------------------------------------------------------------
# DATA WRITING
# ------------------------------------------------------------


# Return all data about specified brick
def create_brick(brick: str):
    return br_brick_list[brick].copy()


# What am I supposed to comment here?
class BRAPI:

    # Getting all values. Do I have to comment that too?
    def __init__(self,
                 bricks=None,
                 project_folder_directory='',
                 project_name='',
                 write_blank=False,
                 project_display_name='',
                 file_description=''):

        # I'm not commenting this either.
        self.project_folder_directory = project_folder_directory  # Path
        self.project_name = project_name  # String
        self.write_blank = write_blank  # Boolean
        self.project_display_name = project_display_name  # String
        self.file_description = file_description  # String
        if bricks is None:  # List (None is used here for initialization)
            bricks = []
        self.bricks = bricks


    # Creating more variables
    # In project path
    @property
    def in_project_folder_directory(self): # String
        return os.path.join(self.project_folder_directory, self.project_name)

    # Calculate brick count
    @property
    def brick_count(self): # 16 Bit integer
        return len(self.bricks)

    # Calculate vehicle size
    @property
    def vehicle_size(self): # List of 3 32-bit float
        # TODO : CALCULATE SIZE
        return [1, 2, 3]

    # Calculate vehicle weight
    @property
    def vehicle_weight(self): # 32 bit float
        # TODO : CALCULATE WEIGHT
        return 0.1

    # Calculate vehicle worth
    @property
    def vehicle_worth(self): # 32 bit float
        # TODO : CALCULATE WORTH
        return 0.2

    # Adding bricks to the brick list
    def add_brick(self, brick_name: str, new_brick: dict):
        self.bricks.append([str(brick_name), new_brick])

        return self


    # Removing bricks from the brick list
    def remove_brick(self, brick_name: str):

        self.bricks = [sublist for sublist in self.bricks if sublist[0] != str(brick_name)]

        return self


    # Updating a currently existing brick
    def update_brick(self, brick_name: str, new_brick: dict):
        self.remove_brick(brick_name)
        self.add_brick(brick_name, new_brick)

        return self


    # Used to create directory for file generators
    def ensure_project_directory_exists(self):

        # Verify for invalid inputs
        if not os.path.exists(self.project_folder_directory):

            raise FileNotFoundError(f'Unable to find the project\'s folder ({self.project_folder_directory})')

        os.makedirs(os.path.dirname(os.path.join(self.in_project_folder_directory, self.project_name)), exist_ok=True)


    # Writing preview.png
    def write_preview(self):

        _write_preview_regular_image_path = os.path.join(_cwd, 'Resources', 'icon_compressed_reg.png') # Path

        # Create folder if missing
        self.ensure_project_directory_exists()

        # Verify the image exists.
        if not os.path.exists(_write_preview_regular_image_path):

            raise FileNotFoundError('Unable to create preview, original image not found.')

        # Copy saved image to the project folders.
        copy_file(os.path.join(_write_preview_regular_image_path),
                  os.path.join(self.in_project_folder_directory, "Preview.png"))


    # Writing metadata.brm file
    def write_metadata(self):

        # Create folder if missing
        self.ensure_project_directory_exists()

        # Verify self.write_blank is valid.
        if not isinstance(self.write_blank, bool):

            raise TypeError('Invalid write_blank type. Expected bool.')

        # Write blank file for metadata (if desired)
        if self.write_blank:

            blank_metadata = open(os.path.join(self.in_project_folder_directory, "MetaData.brm"), "x")
            blank_metadata.close()

        # Otherwise write working metadata file
        else:
            with open(os.path.join(self.in_project_folder_directory, "MetaData.brm"), 'wb') as metadata_file:

                # Writes Carriage Return char
                metadata_file.write(unsigned_int(13, 1))

                # Write all necessary information for the file name
                line_feed_file_name = (((self.project_name.replace("\\n", "\n")).encode('utf-16'))
                                       .replace(b'\x0A\x00',b'\x0D\x00\x0A\x00')).decode('utf-16') # String
                metadata_file.write(signed_int(-len(line_feed_file_name), 2))
                metadata_file.write(bin_str(line_feed_file_name)[2:])

                # Write all necessary information for the file description
                watermarked_file_description = f"Created using BR-API.\n" \
                                               f"BR-API Version {version}.\n\n" \
                                               f"Description:\n{self.file_description}." # String
                watermarked_file_description = (
                    ((watermarked_file_description.replace("\\n", "\n")).encode('utf-16'))
                    .replace(b'\x0A\x00',b'\x0D\x00\x0A\x00')).decode('utf-16') # String
                metadata_file.write(signed_int(-len(watermarked_file_description), 2))
                metadata_file.write(bin_str(watermarked_file_description)[2:])

                # Write all necessary information for the 4 additional values : Bricks, Size, Weight and Monetary Value
                metadata_file.write(signed_int(self.brick_count, 2))
                metadata_file.write(bin_float(self.vehicle_size[0], 4))
                metadata_file.write(bin_float(self.vehicle_size[1], 4))
                metadata_file.write(bin_float(self.vehicle_size[2], 4))
                metadata_file.write(bin_float(self.vehicle_weight, 4))
                metadata_file.write(bin_float(self.vehicle_worth, 4))

                # Writes the author. We don't want it to be listed, so we write invalid data.
                metadata_file.write(bytes.fromhex('FFFFFFFFFFFFFFFF'))

                # I have no fucking clue of what I'm writing but hey it's something right?
                metadata_file.write(bytes.fromhex("14686300000000B034B6C7382ADC08E079251F392ADC08"))

                # Writing tags                                                                                          TODO Broken
                metadata_file.write(unsigned_int(3, 1))
                for i in range(3):
                    metadata_file.write(unsigned_int(5, 1))
                    metadata_file.write(small_bin_str("Other"))


    # Writing Vehicle.brv
    def write_brv(self):

        # Create folder if missing
        self.ensure_project_directory_exists()

        # Verify self.write_blank is valid.
        if not isinstance(self.write_blank, bool):

            raise TypeError('Invalid write_blank type. Expected bool.')

        # Write blank file for vehicle (if desired)
        if self.write_blank:
            blank_brv = open(os.path.join(self.in_project_folder_directory, "Vehicle.brv"), "x")
            blank_brv.close()

        # Otherwise write working vehicle file
        else:

            # Verify if there are too many bricks
            if len(self.bricks) > 65535:

                raise OverflowError('Brick Rigs cannot support more than 65535 bricks. (16 bit int maximum)')

            with open(os.path.join(self.in_project_folder_directory, "Vehicle.brv"), 'wb') as brv_file:


                bricks_writing = self.bricks.copy()

                # Writes Carriage Return char
                brv_file.write(unsigned_int(13, 1))
                # Write brick count
                brv_file.write(unsigned_int(len(bricks_writing), 2))

                # Get the different bricks present in the project
                brick_types = list(set(item[1]['gbn'] for item in bricks_writing)) # List

                # Write the number of different brick types
                brv_file.write(unsigned_int(len(brick_types), 2))


                # [ Getting rid of all properties that are set to the default value for each brick ]
                # Brick list filtering variables
                temp_iebl : list = [] # List of lists containing an integer and a list containing a dictionary and integers
                safe_property_list : list = ['gbn', 'Position', 'Rotation']

                # Defining bricks
                w_current_brick_id : int = 1 # 16 bit
                string_name_to_id_table = {}
                property_table : dict = {}
                property_id_to_property_type_table : dict = {}

                # List Properties
                for current_brick in bricks_writing:

                    # --------------------------------------------------
                    # Getting rid of already existing elements, setting brick IDs
                    # --------------------------------------------------

                    # Add all bricks without including data
                    temp_iebl += [[w_current_brick_id, [{}, {}]]]
                    string_name_to_id_table = string_name_to_id_table | {current_brick[0]: w_current_brick_id}
                    w_current_brick_id += 1

                    # For each data for each brick
                    for p_del_current_key, p_del_current_value in current_brick[1].items():

                        # Accept if it's in the safe list (list which gets whitelisted even if default value is identical)
                        if p_del_current_key in safe_property_list:

                            temp_iebl[-1][1][0][p_del_current_key] = p_del_current_value

                        # Otherwise regular process : if not default get rid of it
                        elif not p_del_current_value == br_brick_list[current_brick[1]['gbn']][p_del_current_key]:

                            # stfu
                            temp_iebl[-1][1][1] = temp_iebl[-1][1][1] | {p_del_current_key: p_del_current_value}

                            # Make sure key in the dict exist
                            property_table.setdefault(p_del_current_key, [])

                            if p_del_current_value not in property_table[p_del_current_key]:
                                property_table[p_del_current_key].append(p_del_current_value)


                # Setup property ids
                w_current_property_id: int = 1  # 16 bit
                id_assigned_property_table: dict = {}

                # Give IDs to all values in var 'id_assigned_property_table'
                for property_value_key, property_value_value in property_table.items():

                    id_assigned_property_table = id_assigned_property_table | {property_value_key: {}}

                    for pvv_value in property_value_value:

                        id_assigned_property_table[property_value_key]: dict = id_assigned_property_table[property_value_key] | {w_current_property_id: pvv_value}
                        w_current_property_id += 1

                # Give IDs
                temp_bricks_writing: list = []

                for current_brick in range(len(bricks_writing)):

                    temp_bricks_writing += [[ temp_iebl[current_brick][0], [temp_iebl[current_brick][1][0], []] ]]

                    # Give Property IDs, Brick Type IDs
                    for current_property, current_property_value in temp_iebl[current_brick][1][1].items():

                        # Find what the id is
                        for key, value in id_assigned_property_table[current_property].items():
                            if value == current_property_value:
                                found_key: int = int(key)

                        # Giving IDs
                        temp_bricks_writing[-1][1][1].append(found_key)

                    # Giving Brick Type IDs
                    temp_bricks_writing[-1][1][0]['gbn'] = brick_types.index(temp_bricks_writing[-1][1][0]['gbn'])

                # Bricks Writing is ready!
                temp_bricks_writing = temp_bricks_writing.copy()

                # Insert n-word here

                # Bricks Writing is ready to be updated!
                bricks_writing = temp_bricks_writing


                # Debug
                print(f'identical : {temp_iebl}')
                print(f'p_t table : {property_table}')
                print(f'iap table : {id_assigned_property_table}')
                print(f'temp bp w : {temp_bricks_writing}')
                print(f'str n->id : {string_name_to_id_table}')
                print(f'bricks t. : {brick_types}')
                print(f'pit table : {property_id_to_property_type_table}')

                # Write how many properties there are
                property_count = w_current_property_id-1
                brv_file.write(unsigned_int(property_count, 2))


                # Write each brick type
                for brick_type in brick_types:
                    brv_file.write(unsigned_int(len(brick_type), 1))
                    brv_file.write(small_bin_str(brick_type))

                temp_spl: bytes = b''

                # Write properties
                for property_type_key, property_type_value in property_table.items():
                    brv_file.write(unsigned_int(len(property_type_key), 1))
                    brv_file.write(small_bin_str(property_type_key))
                    brv_file.write(unsigned_int(len(property_type_value), 2))


                    for property_type_current_value in property_type_value:
                        if isinstance(property_type_current_value, int):
                            temp_spl += unsigned_int(property_type_current_value, 2)
                        if isinstance(property_type_current_value, float):
                            temp_spl += bin_float(property_type_current_value, 4)
                        if isinstance(property_type_current_value, bool):
                            raise_warning(f'Booleans are not supported. Value: {property_type_current_value}')
                            temp_spl += b'\x00\x00'

                    brv_file.write(unsigned_int(len(temp_spl), 4))
                    brv_file.write(temp_spl)
                    temp_spl: bytes = b''  # Reset

                print(f'temp spl. : {temp_spl}')




# Try it out

data = BRAPI()
data.project_name = 'test project b'
data.project_display_name = 'My Project'
data.project_folder_directory = os.path.join(_cwd, 'Projects')
data.file_description = 'My first project.'

print(data.project_folder_directory)

first_brick = create_brick('Switch_1sx1sx1s')
second_brick = create_brick('DisplayBrick')
third_brick = create_brick('Switch_1sx1sx1s')

first_brick['bReturnToZero'] = bool(False)
first_brick['OutputChannel.MinIn'] = float(12)
third_brick['OutputChannel.MaxOut'] = float(-12)
first_brick['OutputChannel.MaxOut'] = float(174)
second_brick['bGenerateLift'] = bool(True)

data.add_brick('first_brick', first_brick)
data.add_brick('second_brick', second_brick)
data.add_brick('third_brick', third_brick)

data.write_preview()
data.write_metadata()
data.write_brv()


"""
# Doesnt matter.
my_test_brick = create_brick('Switch_1sx1sx1s')
data.add_brick('my_test_brick', my_test_brick)
print(my_test_brick)
print(data.bricks)
"""