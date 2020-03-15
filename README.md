# PDF file merger
===

This is a simple flask application to upload your files to your own machine and save them as a new file where all docs are merged *in the order they were uploaded*

I wrote this because you need no silly app to do the same and having your browser as the application to read PDFs, it is also useful to have it as the merging files one.
Configs are not meant to be changed but if you do, mind the following:

`ALLOW_DOWNLOADS` is a boolean flag that will give `/upload` a different behavior. You can download your merged files but you can also store them an call it a day, if you set this flag to `TRUE` you will be redirected and served the file to your browser.

`CRSF` is enabled by default, you should not reuse the same form, instead, go to `/` and click the `Upload` link.