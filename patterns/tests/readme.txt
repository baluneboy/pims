Run these tests after patterns change AND AFTER adding updates/new a test_*.py file.

    #------------------------------------------------
    for alternate test examples using unittest, see:
    ~/dev/programs/python/ugaudio/tests
    #------------------------------------------------

# THIS IS HOW TO RUN THE TESTS
cd ~/dev/programs/python/pims/patterns/tests
python -B -m pytest # ALL FOUND IN THIS DIR

# or

cd ~/dev/programs/python/pims/patterns/tests
python -B -m pytest test_gutwrenchpats.py # JUST ONE FILE
