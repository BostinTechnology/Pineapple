touch shared-local-instance.db

cp dynamodb-master.db.bkup shared-local-instance.db

java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb



