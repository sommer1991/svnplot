#Why SVNplot is slow in updating the database for the first time

# Why SVNplot is slow in updating the database for the first time #
SVNPlot doesnot require  checked out copy of the repository. However, it queries the repository to for 'diff' information of every revision to get the line count data. This process can be really slow if you have very large repository and you are accessing it over network.

Once initial repository database is created, subsequent updates are incremental and hence will be lot faster.

#### There are two options to improve the speed of initial database creation. ####

### 1. Exclude the line count information ###
If you don't need the line count information in donot specify -l (linecount) option to svnlog2sqlite.py. If -l option is not specified then svnlog2sqlite.py will not query the 'diff' for every revision. Hence database creation will be faster.

### 2. Create local mirror and run svnlog2sqlite against local mirror. ###
The diff computation and transfer of 'diff' over network are time consuming operations. The 'svnsync' command used to create local mirror of the repository transfers the data is much more compact form. Once a local mirror is created, svnlog2sqlite.py against the local mirror.
  1. Create local mirror of svn repository on your own computer using 'svnsync'. See [repository replication](http://svnbook.red-bean.com/en/1.5/svn.reposadmin.maint.html#svn.reposadmin.maint.replication)
  1. run 'svnlog2sqlite.py' against the local mirror.
> > svnlog2sqlite.py -g -l <local repo mirror> repodb.sqlite
  1. initial svnplot database (repodb.sqlite) is now ready.
  1. now use the same database and run svnlog2sqlite against the actual repository.
> > svnlog2sqlite.py -g -l <actual repository path> repodb.sqlite
> > This step will update any changes the actual repository that were done AFTER the  repository mirror creation to sqlite dataabse
  1. Now on use the actual repository for incremental updates to sqlite database
  1. You can now delete the locally mirrored repository.
