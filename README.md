
# MailSender

A small SMTP utility for sending newsletter type e-mails to multiple recipients with Python.

It will prior to sending do some sanity checks on the contents as well as test the spammyness of the e-mail by using an external service.
This to help you **not getting flagged as spam**, which you really do not want.

## Limitations

* Currently only supports plain text, HTML e-mails are scary.
* Chose not implements file attachments, which increases spammyness. Just paste a link to files hosted online instead.

## Usage

Clone the repo and run `send.py` from the command-line.

```
python send.py --config=myconfig.yml --to=recipients.txt --subject="Newsletter 2019" --plain=plain_text_body.txt
```
