
# Load dynamodb in a seperate window
lxterminal -e java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -inMemory

# Run the pyuthon script to load sample data into it.
python3 ./TableUtilities/CreateTables.py

node .



