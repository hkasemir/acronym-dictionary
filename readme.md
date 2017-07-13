# WTF does that mean?
_For people who don't know all the TLAs_

This is a dictionary of acronyms to help people on your team communicate!
Teams often have a shorthand that can sometimes be confusing. At Udacity,
we have NDOPs, SSRs and CDs for example, and in case you don't know that
these mean "Nanodegree Overview Pages", "Student Support Representative",
or "Content Developer" - you might be SOL...

## Database Design

Users will authenticate with github, since pretty much everyone at Udacity is
encouraged to learn to code!

The user table has
```
uid | username | hashed_token
```
users will be added when they authenticate and their browsers cookies will keep
the session open

the definition table has
```
id | word | definition | created_by | category
```
any user can create a new entry, but items will only be editable by those who
created them

there will be categories for different types of acronyms (i.e. 'slang', 'job', 'component')
the category table has:
```
id | name
```
anybody can create a category, nobody can edit a category, and anyone can delete
a category that has no words associated with it.


## To run locally

set up vagrant and virtual box following instructions from Udacity's full stack
[vm](https://github.com/udacity/fullstack-nanodegree-vm)

once you're in, set up the database by running 
```
python models.py
```

you'll need to add an OAuth application on github (sorry, I'm not sharing my secrets)
and include a new `secrets.json` file with the following format: 
```
{
  "client_id": "your id",
  "client_secret": "your secret"
}
```
in the root directory
