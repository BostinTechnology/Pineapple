# This will download the required sqlite4java source for the ARM device and compile it to form a working dynamoDB 


# wget https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/sqlite4java/source-archive.zip

# wget https://raw.github.com/SpatialInteractive/sqlite4java-custom/master/custom/swig/sqlite_wrap.c

wget https://s3.eu-central-1.amazonaws.com/dynamodb-local-frankfurt/dynamodb_local_latest.tar.gz

tar -xvf ./dynamodb_local_latest.tar.gz

mv ./libsql* ./DynamoDBLocal_lib/



# unzip ./source-archive.zip 

# mv sqlite_wrap.c ./sqlite4java/trunk/
 
#cd ./sqlite4java/trunk/


# Now build gcc
#gcc -O2 -DNDEBUG -fpic -DARM -DARCH="ARM" -DLINUX -D_LARGEFILE64_SOURCE -D_GNU_SOURCE -D_LITTLE_ENDIAN -fno-omit-frame-pointer -fno-strict-aliasing -static-libgcc -I./sqlite -I/usr/lib/jvm/jdk-7-oracle-armhf/include -I/usr/lib/jvm/jdk-7-oracle-armhf/include/linux -DSQLITE_ENABLE_COLUMN_METADATA -DSQLITE_ENABLE_FTS3 -DSQLITE_ENABLE_FTS3_PARENTHESIS -DSQLITE_ENABLE_MEMORY_MANAGEMENT -DSQLITE_ENABLE_STAT2 -DHAVE_READLINE=0 -DSQLITE_THREADSAFE=1 -DSQLITE_THREAD_OVERRIDE_LOCK=-1 -DTEMP_STORE=1 -DSQLITE_OMIT_LOAD_EXTENSION=1 -DSQLITE_OMIT_DEPRECATED -DSQLITE_OS_UNIX=1 -c ./sqlite/sqlite3.c -o sqlite3.o
#gcc -O2 -DNDEBUG -fpic -DARM -DARCH="ARM" -DLINUX -D_LARGEFILE64_SOURCE -D_GNU_SOURCE -D_LITTLE_ENDIAN -fno-omit-frame-pointer -fno-strict-aliasing -static-libgcc -I./sqlite -I/usr/lib/jvm/jdk-7-oracle-armhf/include -I/usr/lib/jvm/jdk-7-oracle-armhf/include/linux -DSQLITE_ENABLE_COLUMN_METADATA -DSQLITE_ENABLE_FTS3 -DSQLITE_ENABLE_FTS3_PARENTHESIS -DSQLITE_ENABLE_MEMORY_MANAGEMENT -DSQLITE_ENABLE_STAT2 -DHAVE_READLINE=0 -DSQLITE_THREADSAFE=1 -DSQLITE_THREAD_OVERRIDE_LOCK=-1 -DTEMP_STORE=1 -DSQLITE_OMIT_LOAD_EXTENSION=1 -DSQLITE_OMIT_DEPRECATED -DSQLITE_OS_UNIX=1 -c sqlite_wrap.c -o sqlite_wrap.o
#gcc -O2 -DNDEBUG -fpic -Di586 -DARCH="i586" -DLINUX -D_LARGEFILE64_SOURCE -D_GNU_SOURCE -D_LITTLE_ENDIAN -fno-omit-frame-pointer -fno-strict-aliasing -static-libgcc -I./sqlite -I./native -I/usr/lib/jvm/jdk-7-oracle-armhf/include -I/usr/lib/jvm/jdk-7-oracle-armhf/include/linux -DSQLITE_ENABLE_COLUMN_METADATA -DSQLITE_ENABLE_FTS3 -DSQLITE_ENABLE_FTS3_PARENTHESIS -DSQLITE_ENABLE_MEMORY_MANAGEMENT -DSQLITE_ENABLE_STAT2 -DHAVE_READLINE=0 -DSQLITE_THREADSAFE=1 -DSQLITE_THREAD_OVERRIDE_LOCK=-1 -DTEMP_STORE=1 -DSQLITE_OMIT_LOAD_EXTENSION=1 -DSQLITE_OMIT_DEPRECATED -DSQLITE_OS_UNIX=1 -c ./native/sqlite3_wrap_manual.c -o sqlite3_wrap_manual.o
#gcc -O2 -DNDEBUG -fpic -Di586 -DARCH="i586" -DLINUX -D_LARGEFILE64_SOURCE -D_GNU_SOURCE -D_LITTLE_ENDIAN -fno-omit-frame-pointer -fno-strict-aliasing -static-libgcc -I./sqlite -I./native -I/usr/lib/jvm/jdk-7-oracle-armhf/include -I/usr/lib/jvm/jdk-7-oracle-armhf/include/linux -DSQLITE_ENABLE_COLUMN_METADATA -DSQLITE_ENABLE_FTS3 -DSQLITE_ENABLE_FTS3_PARENTHESIS -DSQLITE_ENABLE_MEMORY_MANAGEMENT -DSQLITE_ENABLE_STAT2 -DHAVE_READLINE=0 -DSQLITE_THREADSAFE=1 -DSQLITE_THREAD_OVERRIDE_LOCK=-1 -DTEMP_STORE=1 -DSQLITE_OMIT_LOAD_EXTENSION=1 -DSQLITE_OMIT_DEPRECATED -DSQLITE_OS_UNIX=1 -c ./native/intarray.c -o intarray.o
#gcc -O2 -DNDEBUG -fpic -Di586 -DARCH="i586" -DLINUX -D_LARGEFILE64_SOURCE -D_GNU_SOURCE -D_LITTLE_ENDIAN -fno-omit-frame-pointer -fno-strict-aliasing -static-libgcc -shared -mno-cygwin -Wl,-soname=libsqlite4java-linux-arm.so -o libsqlite4java-linux-arm.so sqlite3.o sqlite_wrap.o sqlite3_wrap_manual.o intarray.o




