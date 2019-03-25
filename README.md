GitHub/G Suite user sync
========================

Are you using G Suite as a user directory? Do you want to simplify your
process for handling joiners/leavers to your organisation? Are you also using
GitHub?

This project provides a script that will synchronise membership of a group
on GitHub.com (premium GitHub and Enterprise Edition have other mechanisms for
single sign-on that may be more suitable).

It does this by having a custom attribute in your G Suite directory that
corresponds to a GitHub username, and inviting those users to your GitHub
org if they are not already a member. If you have any members of your group
who do not have a username recorded against a corresponding user in your G
Suite Directory will be removed from your organisation.

Getting started
---------------

1. Install this script:
   * Classic way: `python3 setup.py install`
   * Docker way: `docker build -t 1500cloud/github-user-sync:latest .`

2. You will need to create a new field in your G Suite directory to hold the
   relevant GitHub usernames.
   1. Go to https://admin.google.com/u/1/ac/customschema
   2. Select 'Add a Custom Attribute' (or if you have a category called
      'External Services' already, edit it)
   3. Name the Category 'External Services' and under custom fields create a
      field with name 'GitHub username', type text, 'visible to admin' and
      single value (case is important in both cases)

3. You will need to create a service account to allow the script to read from
   your G Suite directory. [Follow Google's docs to create a service account](https://support.google.com/a/answer/7378726?hl=en),
   and ensure that the Admin SDK is enabled. Make a note of the client ID, and
   download the service account credentials file in JSON form. Keep this
   secret.
   
4. Enable the service account to read from your Directory. Go to [Manage API client access](https://admin.google.com/AdminHome?chromeless=1#OGX:ManageOauthClients)
   and add an entry with the Client Name being the ID (long number string) of
   the service account, and the API scope `https://www.googleapis.com/auth/admin.directory.user.readonly`.

5. Use the G Suite users panel to populate the appropriate users with their
   GitHub usernames.

6. [Find out your G Suite customer ID](https://stackoverflow.com/questions/33493998/how-do-i-find-the-immutable-id-of-my-google-apps-account) and make a note of it.

6. Create a personal API token in GitHub.com for someone who is an
   administrator of the org. Also keep this secret.

7. Run the script. Configuration options are passed as environment variables.
   * Classic way:
     ```
     GOOGLE_CREDENTIALS_PATH=credentials.json \
     GOOGLE_ADMINISTRATOR_ACCOUNT=administrator@example.com \
     GOOGLE_CUSTOMER_ID=C12345678 \
     GITHUB_ACCESS_TOKEN=ABCDEFABCEDF \
     GITHUB_ORG=myorg \
     sync-github-users
     ```
   * Docker way:
     ```
     docker run -e GOOGLE_CREDENTIALS_PATH=/secrets/credentials.json \
                -e GOOGLE_ADMINISTRATOR_ACCOUNT=administrator@example.com \ 
                -e GOOGLE_CUSTOMER_ID=C12345678 \
                -e GITHUB_ACCESS_TOKEN=ABCDEFABCEDF \
                -e GITHUB_ORG=myorg \
                --mount src=/root/secrets/user-sync/,dst=/secrets/,readonly=true,type=bind \
                1500cloud/github-user-sync:latest
     ```

   Any changes that have been made are printed out to the terminal.
   As a get out clause, if the script thinks that every member who is
   currently in the GitHub org should be removed, it will exit without doing
   anything.
