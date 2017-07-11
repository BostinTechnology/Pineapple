Install boto3 & aws cli interfacea on a raspberry pi

    sudo pip3 install boto3

    sudo pip3 install awscli --upgrade --user


this will put the tools on the Pi to interfacae with dynamodb.

I have downloaded dynamodb to the Mac to run it independently from the Pi. To start it running:-

    java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -inMemory
    
This creates a version running in memory, no data saved.

To access the local console type:
    http://localhost:8000/shell/
    
    one in the console click on </> and it will give a list of standard commands you can run. Choose the one you want, click 
    on << and the to run it click on the triangle button

Running CreateTables.py will then create the tables.

    ** Set the IP address of the dynamodb

Javascript local example

http://docs.aws.amazon.com/amazondynamodb/latest/gettingstartedguide/GettingStarted.JavaScript.html

