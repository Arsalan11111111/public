# Mail Multi Domain Module Odoo
This module allows you tu use different email domain aliases in Odoo.

## Technical parameters

---

There are several configuration parameters depending on your needs.

* If you want to use different servers by user, a system parameter must be configured.

        Key = mail.split_server_mail_by_user
        Value = True

* If you want to use different signatures depending on your email addresses, a new system parameter must be configured.
        
        Key = mail.split_server_mail_by_user
        Value = False

        Key = mail.use_different_signature
        Value = True

## Functional parameters

---

### Different servers by user
If you want to use different servers by user, follow the next steps on debug mode:
1. Go to Configuration > Technical > System Parameters > and select **mail.split_server_mail_by_user** to set the value to **True**.
2. Go to Configuration > Technical > Outgoing Mail Servers
3. Configure your outgoing mail servers. Do not forget to indicate your alias domain.
4. Go to Users & Companies > Users > Preferences > indicate server mail.

At this stage, your users can send email with this address **email_address@alias_domain** of server chosen.

*If you want, you can specify the server mail directly on the companies : Users & Companies > Companies > and indicate alias domain mail. And your users will use the server of their default company but you must ignore the step 4.*


        Example: 
        User: John Doe
        Email address: john_doe@test

        User: Alex Doe
        Email address: john_doe@test2

        Servers: test | test2

> You have two outgoing mail servers but Odoo uses everytime the first server and there is no problem with John Doe, but with Alex Doe, you want to use the second server. Therefore, This module makes possible the use of the right server for each user.

---

### Different alias domain (not by user)
If you want to change domain for your email address (easily):
1. Go to Configuration > Technical > System Parameters and set the parameters **mail.split_server_mail_by_user** and **mail.use_different_signature** values to **False**.
2. Go to Configuration > Technical > Outgoing Mail Servers
3. Configure your outgoing mail servers. Do not forget to indicate your alias domain.
4. Go to Users & Companies > Companies and configure your companies to indicate the alias domain.

*If you want to use many email addresses, go to Users > Preferences and you have a table to register your email addresses with their alias domain.*

        Example:
        User: John Doe
        Email address: johndoe@example.com

        Server with alias domain: test.com

> So, when you send an email, the email address will not be johndoe@example.com but johndoe@test.com

---

### Change signature when using an email address
If you want to have one signature by email address, follow next steps:
1. Go to Configuration > Technical > System Parameters and active the next parameters:
        
        Key = mail.split_server_mail_by_user
        Value = False

        Key = mail.use_different_signature
        Value = True

2. Go to Configuration > Technical > Outgoing Mail Servers
3. Configure your outgoing mail servers. Do not forget to indicate your alias domain.
4. Go to Configuration > Users & Companies > Users > Preferences and add into the table your email address, alias domain and signatures.
5. Go to Configuration > Users & Companies > Companies and add an alias domain.

        Example:
        | Name |       Email         |   Alias domain   |    Signature  |
        | John | johndoe@example.com |  example.com     | John Example. |
        | John | johndoe@test.com    |  test.com        | John Testing  |

        User: John Doe
        Alias domain on the default company: test.com

> When you use an alias domain on the company, the user will be able to use the signature configured with the alias domain.
