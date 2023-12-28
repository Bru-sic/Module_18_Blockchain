# PyChain Ledger
#
# Revised by Bruno Ivasic 28/12/2023
# * Changed dates to ISO 8601 "Z" format
# * Created the Record data class
# * Capture user inputs for Sender, Reciever and Amount
# * Implement caching
# * Implemented address book from which sender and receiver are selected
# * Show Sender / Receiver avatars
# * Repositioned the Difficulty slider to the main page
# * Removed "balloons" widget, instead used "toast" status to indicate completion of Validate Block and Add Block
# * Disable Add Block button if sender or receiver are not selected, or the amount is 0.00
# * Replace Block Inspector selectbox with Slider
# * Present Block Inspector selected block using markdown table rather than the st.write to avoid method commentary being presented
# * Located push buttons in close proximity.



# Briefing
################################################################################
# You’ll make the following updates to the provided Python file for this
# Challenge, which already contains the basic `PyChain` ledger structure that
# you created throughout the module:

# Step 1: Create a Record Data Class
# * Create a new data class named `Record`. This class will serve as the
# blueprint for the financial transaction records that the blocks of the ledger
# will store.

# Step 2: Modify the Existing Block Data Class to Store Record Data
# * Change the existing `Block` data class by replacing the generic `data`
# attribute with a `record` attribute that’s of type `Record`.

# Step 3: Add Relevant User Inputs to the Streamlit Interface
# * Create additional user input areas in the Streamlit application. These
# input areas should collect the relevant information for each financial record
# that you’ll store in the `PyChain` ledger.

# Step 4: Test the PyChain Ledger by Storing Records
# * Test your complete `PyChain` ledger.

################################################################################
# Imports
import streamlit as st
from dataclasses import dataclass
from typing import Any, List
import datetime as datetime
import pandas as pd
import hashlib

import os
from pathlib import Path


################################################################################
# Define constants
images_base_path = "../Images/"               # Base folder where the user photos are found
no_image_fn = images_base_path + "none.png"   # Image filename used when user is not yet specified

################################################################################
# Define variables
sender_name = None         # Set the sender's name to none to load the none.png image prior to section
receiver_name = None       # Set the receiver's name to none to load the none.png image prior to section
amount = 0.0               # Intialise the amount to 0

addressbook=[
	{   "user_name": "Chantalle",
		"user_id"  :33,
		"image_fn" : "chantalle.png",	},
	{
		"user_name": "Manny Riskin",
		"user_id"  :12,
		"image_fn" : "manny.png",	},
	{
		"user_name": "Jordan Belfort",
		"user_id"  :68,
		"image_fn" : "jordan.png",	},
	{
		"user_name": "Leah Belfort",
		"user_id"  :42,
		"image_fn" : "leah.png",	},
	{
		"user_name": "Aunt Emma",
		"user_id"  :59,
		"image_fn" : "emma.png",	}
]

address_book_df = pd.DataFrame(addressbook)
address_book_df.reset_index()
################################################################################
# Step 1:
# Create a Record Data Class

# Create a Record Data Class that consists of the `sender`, `receiver`, and
# `amount` attributes
@dataclass
class Record:
    sender: str             
    receiver: str
    amount: float



################################################################################
# Step 2:
# Modify the Existing Block Data Class to Store Record Data

@dataclass
class Block:
    """Creates a Block Chain block object\n\n

    Parameters arguments:\n
    record -- the record of data to be stored in the block\n
    creator_id -- the ID of the Creator\n
    prev_hash -- the has of the previous block in the chain. Default: "0"\n
    nonce -- the nonce for the block. Default: 0
    """
    record: Record
    creator_id: int
    prev_hash: str = "0"
    timestamp: str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # Use the full ISO 8601 date and time format YYYY-MM-DDTHH:MM:SS.ssssssZ 
    nonce: int = 0

    def hash_block(self):
        """Returns the sha hash digest in hexadecimal of the class attributes."""
        sha = hashlib.sha256()

        record = str(self.record).encode()
        sha.update(record)

        creator_id = str(self.creator_id).encode()
        sha.update(creator_id)

        timestamp = str(self.timestamp).encode()
        sha.update(timestamp)

        prev_hash = str(self.prev_hash).encode()
        sha.update(prev_hash)

        nonce = str(self.nonce).encode()
        sha.update(nonce)

        return sha.hexdigest()
    
# PyChain Class
@dataclass
class PyChain:
    chain: List[Block]
    difficulty: int = 4

    # PyChain Proof Of Work method - returns a block with a hash meeting the difficulty target
    def proof_of_work(self, block):
        calculated_hash = block.hash_block()

        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):

            block.nonce += 1

            calculated_hash = block.hash_block()

        return block

    # PyChain Add Block method - calls proof of work and then adds a block to the PyChain
    def add_block(self, candidate_block):
        block = self.proof_of_work(candidate_block)
        self.chain += [block]

    # PyChain Is Valid method - runs through each block in the PyChain and checks the validity of the hash. Returns false at the first invalid hash or true if all are valid
    def is_valid(self):
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()

        print("Blockchain is Valid")
        return True


# Helper function to initialise the PyChain 
@st.cache_resource()
def setup():
    print("Initializing Chain")
    return PyChain([Block("Genesis", 0)])

# Helper function to initialise cache session variables 
@st.cache_resource()
def init_vars():
    if "sender" not in st.session_state:
        st.session_state.sender = None

    if "receiver" not in st.session_state:
        st.session_state.receiver = None

    if "amount" not in st.session_state:
        st.session_state.amount = 0.0

    if "add_block_button_enabled" not in st.session_state:
        st.session_state.add_block_button_enabled = user_inputs_complete()

# Helper function to determine if user inputs are complete.
def user_inputs_complete():
    """Returns True If all user inputs are valid and complete Else returns False""" 
    return ((st.session_state.sender != None) and      
            (st.session_state.receiver != None) and
            (st.session_state.amount != 0.0))

# Event handler called when Sender has been changed in the select box widget
def sender_changed():
    sender_name = st.session_state.sender                               # Extract the current values of the amount widget
    st.session_state.add_block_button_enabled = user_inputs_complete()  # Determine if the "Add Block" button should change state to enabled or disabled

# Event handler called when Receiver has been changed in the select box widget
def receiver_changed():
    receiver_name = st.session_state.receiver                           # Extract the current values of the receiver widget
    st.session_state.add_block_button_enabled = user_inputs_complete()  # Determine if the "Add Block" button should change state to enabled or disabled

# Event handler called when the Amount has been changed in the number input widget
def amount_changed():
    amount = st.session_state.amount                                    # Extract the current values of the amount widget
    st.session_state.add_block_button_enabled = user_inputs_complete()  # Determine if the "Add Block" button should change state to enabled or disabled


###########################################################################################################
# Step 3:
# Caputure User Inputs via Streamlit Graphical User Interface (GUI) Application Programming Interface (API)
###########################################################################################################

# Setup the Pychain blockchain (ie create Genesis block)
pychain = setup()

# Initialise variables
init_vars()

# Display the App's title using the markdown widget
st.markdown("**PyChain**")

# Define an upper zone and a lower zone on the screen realestate 
upper_zone = st.container(border=True)
lower_zone = st.container(border=True)

# Display the section title using the markdown widget
upper_zone.markdown("**Store a Transaction Record in the PyChain**")

# Divide the top section into two columns
uz_top_left, uz_top_right = upper_zone.columns(2)

# Create a zone related to capturing the sender details
sender_details = uz_top_left.container(border=True)
sender_details_left, sender_details_right = sender_details.columns([3, 1])  # Create columns at a ratio of 3:1 so the select box and the avatar on the same row
sender_selectbox_placeholder = sender_details_left.empty()       # As widgets are placed in order of instantiation, create a place-holder so it goes where we want
sender_image_placeholder = sender_details_right.empty()          # As widgets are placed in order of instantiation, create a place-holder so it goes where we want

# Create a zone related to capturing the receiver details
receiver_details = uz_top_left.container(border=True)
receiver_details_left, receiver_details_right = receiver_details.columns([3, 1])  # Create columns at a ratio of 3:1 so the select box and the avatar on the same row
receiver_selectbox_placeholder = receiver_details_left.empty()   # As widgets are placed in order of instantiation, create a place-holder so it goes where we want
receiver_image_placeholder = receiver_details_right.empty()      # As widgets are placed in order of instantiation, create a place-holder so it goes where we want   

# Create a zone for the amount entry / selection with a border
amount_details = uz_top_right.container(border=True)

# Create a zone for the difficulty target entry / selection with a border
difficulty_section = uz_top_right.container(border=True)

# Segment the upper zone further to place the push buttons so that they are roughly centered horizontally
mid_a, mid_b, mid_c = upper_zone.columns([0.3, 0.2, 0.5])   # Column widths of 30%, 20% and 50% allows the push buttons to sit neatly


###########################################################################################################
# Capture the Sender and show their image
###########################################################################################################

# Check if the cached sender is in the address book
sender_addr_bk_details = address_book_df[address_book_df["user_name"]==st.session_state.sender]

# Deterimine the sender image to display
if len(sender_addr_bk_details) == 0:  # If user is not in the address book then use the default "no user image"
    sender_select_index = None
    sender_image_fn = no_image_fn
else:  # Fetch the image associated with the sender
    # Determine the address book's index value to use as an index in the selectbox, so that the selected value matches up with the current selection (mainly for restarts)
    sender_select_index = int(address_book_df[address_book_df["user_name"]==st.session_state.sender].index[0])

    # Join user's image filename to the base images path
    sender_image_fn = images_base_path + sender_addr_bk_details["image_fn"].values[0]

# Display the sender's image or no user as the case may be
sender_image_placeholder.image(str(sender_image_fn), width=64)   # Note: using str as st.image was getting confused that the filename was a bytearray of an image

# Get the Sender's name using a selectbox in the placeholder created earlier
sender_name = sender_selectbox_placeholder.selectbox(   
    "SELECT SENDER",                        # Set the label
    address_book_df["user_name"],           # Load the user names from the address book
    index=sender_select_index,              # Default the selectbox to the currently selected user
    key='sender',                           # Name the widget so we can also reference its value using st.session_state
    placeholder="Select sender...",         # Set the placeholder text shown in the combobox when nothing is selected
)
st.session_state.add_block_button_enabled = user_inputs_complete() # Update the Add Block enabled/disabled status

###########################################################################################################
# Capture the Receiver and show their image
###########################################################################################################

# Check if the cached receiver is in the address book
receiver_addr_bk_details = address_book_df[address_book_df["user_name"]==st.session_state.receiver]

# Deterimine the receiver image to display
if len(receiver_addr_bk_details) == 0: # If user is not in the address book then use the default "no user image"
    receiver_select_index = None
    receiver_image_fn = no_image_fn
else:  # Fetch the image associated with the receiver
    # Determine the address book's index value to use as an index in the selectbox, so that the selected value matches up with the current selection (mainly for restarts)
    receiver_select_index = int(address_book_df[address_book_df["user_name"]==st.session_state.receiver].index[0])

    # Join user's image filename to the base images path
    receiver_image_fn = images_base_path + receiver_addr_bk_details["image_fn"].values[0]

# Display the image
receiver_image_placeholder.image(str(receiver_image_fn))   # Note: using str as st.image was getting confused that the filename was a bytearray of an image and getting an error

# Get the receiver's name using a selectbox in the placeholder created earlier
receiver_name = receiver_selectbox_placeholder.selectbox(   
    "SELECT RECEIVER",                        # Set the label
    address_book_df["user_name"],             # Load the user names from the address book
    index=receiver_select_index,              # Default the selectbox to the currently selected user
    key='receiver',                           # Name the widget
    placeholder="Select receiver...",         # Set the placeholder text shown in the combobox when nothing is selected
)
st.session_state.add_block_button_enabled = user_inputs_complete() # Update the Add Block enabled/disabled status

# Input the amount using number_input in the amount_details section
if amount_details.number_input("ENTER / SELECT ($) AMOUNT",
    min_value=0.00,
    max_value=None,
    #value=st.session_state.amount,
    key="amount",
    step=None,
    format="%0.2f",
    placeholder="Enter or select an amount...",
    on_change=amount_changed()
):
    st.session_state.add_block_button_enabled = user_inputs_complete()  # Update the Add Block enabled/disabled status
    
# Show the Add Block button which when pressed adds a new block to the pychain
if mid_b.button(chr(0x00A0) * 4 + "Add Block " + chr(0x00A0) * 3,   # Pad the label with non-breaking spaces (x000A) so it is roughly the same size as the other button
                         help ="Adds a new block to the PyChain Ledger",     # Set the button's helper text
                         key='add_block',                                    # Name the button
                         disabled= not user_inputs_complete()                # Set the disabled status of the button based on whether all required inputs have been met
                         ):
    with mid_a.status('**Adding block**'): # Show a status widget while the block is being added. Useful if difficulty is set high
        # Add the new block, but before we do, we need to get the hash of the previous block so we can include in with the new block to create the block chain's link

        prev_block = pychain.chain[-1] # Fetch the previous chain
        prev_block_hash = prev_block.hash_block() # Calculate the hash of the previous block

        # Create a new Block with the sender, receiver, amount as the Block's record
        new_block = Block( record=Record( sender=st.session_state.sender,
                                            receiver=st.session_state.receiver,
                                            amount=st.session_state.amount
                                        ),
                            creator_id=sender_addr_bk_details["user_id"].values[0],
                            prev_hash=prev_block_hash
                        ) 
        pychain.add_block(new_block)  # Add the new block to the ledger

    # Notify user that the block has been added via the toast widget
    st.toast(f"{datetime.datetime.utcnow().isoformat()}: Created Block From: {st.session_state.sender} To: {st.session_state.receiver} Amount: ${st.session_state.amount:0.2f} Reference: {new_block.hash_block()}",
             icon="✅")

# Show the Validate Chain button which when clicked validates the pychain and provides the results to the user via the toast widget
if mid_c.button("Validate Chain", help = "Validates the blocks in the PyChain Ledger"):
    if pychain.is_valid():
        st.toast(':green[Chain validation passed]', icon="✅")
    else:
        st.toast(':red[Chain validation failed]', icon="🚨")

# Capture the hash generation difficulty target  (number of leading zeroes needed in the generated hash)
pychain.difficulty = difficulty_section.number_input("ENTER / SELECT DIFFICULTY TARGET",
    min_value=1,      #
    max_value=5,
    value=2,          # Default value when the widget first renders
    step=1,
    format="%0d",
    placeholder="Enter or select the difficulty target..."
)

# Show the contents of the pychain as a dataframe in the lower zone of the screen
with lower_zone:
    st.markdown("**The PyChain Ledger**")
    pychain_df = pd.DataFrame(pychain.chain).astype(str)

    st.dataframe( pychain_df, hide_index=False)

###########################################################################################################
# Sidebar     
###########################################################################################################
    
st.sidebar.markdown("**Block Inspector**")

# Sliders don't work if the min is equal to the max values, so if there is only the genesis record skip selection
if len(pychain.chain) > 1: # If there more than one record in the chain, then allow user to select via the slider widget
    selected_block = st.sidebar.slider(
        "SELECT BLOCK TO INSPECT",
        min_value=0,
        max_value=len(pychain.chain)-1,
        value=None
    )
else:
    selected_block = 0 # default to the genesis record when only 1 record

# The Streamlit dataframe output includes details of methods and field types which are not desired.
# Instead, use Streamlit's markdown widget to output a table using Git-Hub's Flavoured Markdown notation

# Construct a string of markdown to output a formatted table which we can control what gets displayed (ie no method or class text output)
md_text = "|**Field**|**Value**|\r\n|---|---|\r\n"
md_text += f"|Record #:|{selected_block:,}|\r\n"
md_text += f"|Created:|{pychain.chain[selected_block].timestamp}|\r\n"
md_text += f"|Creator Id:|{pychain.chain[selected_block].creator_id}|\r\n"
md_text += f"|Previous Hash:|{pychain.chain[selected_block].prev_hash[0:32]}{chr(0x200B)}{pychain.chain[selected_block].prev_hash[32:]}|\r\n" # Split the hash as it is too long
md_text += f"|Nonce:|{pychain.chain[selected_block].nonce:,}|\r\n"
if selected_block == 0:
    md_text += f"|Record:|{pychain.chain[selected_block].record}|\r\n"
else:
    md_text += f"|Sender:|{pychain.chain[selected_block].record.sender}|\r\n"
    md_text += f"|Receiver:|{pychain.chain[selected_block].record.receiver}|\r\n"
    md_text += f"|Amount:|{pychain.chain[selected_block].record.amount:0,.2f}|\r\n"

# Show the block's data in a table as markdown 
st.sidebar.markdown(md_text)

################################################################################
# Step 4:
# Test the PyChain Ledger by Storing Records

# Test your complete `PyChain` ledger and user interface by running your
# Streamlit application and storing some mined blocks in your `PyChain` ledger.
# Then test the blockchain validation process by using your `PyChain` ledger.
# To do so, complete the following steps:

# 1. In the terminal, navigate to the project folder where you've coded the
#  Challenge.

# 2. In the terminal, run the Streamlit application by
# using `streamlit run pychain.py`.

# 3. Enter values for the sender, receiver, and amount, and then click the "Add
# Block" button. Do this several times to store several blocks in the ledger.

# 4. Verify the block contents and hashes in the Streamlit drop-down menu.
# Take a screenshot of the Streamlit application page, which should detail a
# blockchain that consists of multiple blocks. Include the screenshot in the
# `README.md` file for your Challenge repository.

# 5. Test the blockchain validation process by using the web interface.
# Take a screenshot of the Streamlit application page, which should indicate
# the validity of the blockchain. Include the screenshot in the `README.md`
# file for your Challenge repository.
