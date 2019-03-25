# github-user-sync: synchronises users between G Suite and a GitHub organisation
# Copyright (C) 2019 1500 Services Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from github import Github, UnknownObjectException
from google.oauth2 import service_account
from googleapiclient.discovery import build

LOGGER = logging.getLogger(__name__)


def build_directory_service(service_account_file_path, administrator_email):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file_path,
        scopes=['https://www.googleapis.com/auth/admin.directory.user.readonly']
    ).with_subject(administrator_email)

    return build('admin', 'directory_v1', credentials=credentials)


def fetch_expected_github_users(directory_service, customer_id):
    expected_users = {}
    request = directory_service.users().list(
        customer=customer_id,
        projection='full',
        query='isSuspended=false',
    )
    while request is not None:
        response = request.execute()
        expected_users.update({
            user['customSchemas']['External_Services']['GitHub_username']: user['primaryEmail']
            for user in response.get('users', [])
            if user['customSchemas'].get('External_Services', {}).get('GitHub_username') is not None
        })
        request = directory_service.users().list_next(request, response)
    return expected_users


def build_github_service(access_token):
    return Github(access_token)


def fetch_actual_github_users(org):
    members = org.get_members()
    return {member.login: member for member in members}


def main(google_credentials_path, google_administrator_email, google_customer_id, github_access_token, github_org_id):
    directory_service = build_directory_service(google_credentials_path, google_administrator_email)
    github_service = build_github_service(github_access_token)
    github_org = github_service.get_organization(github_org_id)

    gsuite_users = fetch_expected_github_users(directory_service, google_customer_id)
    github_members = fetch_actual_github_users(github_org)

    if len(set(gsuite_users.keys()) & set(github_members.keys())) == 0:
        raise RuntimeError(
            "There are no users in common between the G Suite Directory and GitHub. Refusing to do anything, "
            "as this is likely to lead to losing access to the GitHub account "
        )

    for user_to_remove in set(github_members.keys()) - set(gsuite_users.keys()):
        LOGGER.info(
            "Removing user {} from GitHub org {} (no corresponding directory entry)".format(user_to_remove, github_org.name)
        )
        github_org.remove_from_members(github_members[user_to_remove])

    for user_to_add in set(gsuite_users.keys()) - set(github_members.keys()):
        try:
            github_user = github_service.get_user(user_to_add)
        except UnknownObjectException:
            LOGGER.warning(
                'GitHub user {} for {} was not found in GitHub'.format(user_to_add, gsuite_users[user_to_add])
            )
            continue

        LOGGER.info(
            "Adding user {} to GitHub org {} (belonging to {})".format(user_to_add, github_org.name, gsuite_users[user_to_add])
        )
        github_org.add_to_members(github_user)

