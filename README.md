## This contains python code to generate a list of id's a linux system and their authorization
## Done for 'auditability' on id's

The program reads the /etc/passwd and /etc/group files to get system id's and their groups, any id
with an id number &lt; 1000 is assumed to be a cloud id (system).  The other id's should be addressed.
What you'd typically do is:
- run the program, it will show the id's that it calls 'Unknown' (ones with) id < 1000
- research those id's and then add them to a file called userInfo.txt (look at variable historyFields
to see layout of file)
- run program again till nothing's reported as unknown

- Review the applications id's installed on the server and create a file called 'applicationIds.txt', the
format of that file is the same as the output from the program (with , as separator).

- Run the program and pipe the output to a '.csv' file, then open that file with a spreadsheet 
package and format it to be pretty.

- Send file to whomever needs it.

### Note this is really just a quick and dirty tool to perform repetitive tasks, it could be made into 
better code but it didn't warrant it at the current time.