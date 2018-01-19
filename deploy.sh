cd src
zappa package
ZIPFILE=`ls *.zip`
echo "Uploading $ZIPFILE"
aws lambda update-function-code --function-name $LAMBDA_FUNCTION --zip-file fileb://$ZIPFILE
rm *.zip
cd ..