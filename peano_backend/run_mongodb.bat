mkdir %~dp0data
mkdir %~dp0data\db
"%~dp0mongodb\bin\mongod.exe" --dbpath "%~dp0data\db"