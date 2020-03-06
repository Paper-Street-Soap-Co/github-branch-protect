# github-branch-protect

![protected-branch](https://i.ibb.co/s2SKDkD/158351852060458681.png)

![build](https://github.com/Paper-Street-Soap-Co/github-branch-protect/workflows/build/badge.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/Paper-Street-Soap-Co/github-branch-protect/badge.svg?branch=master)](https://coveralls.io/github/Paper-Street-Soap-Co/github-branch-protect?branch=master)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Github Branch Protect Microservice with Google Cloud Functions

## Keep branches protected from start!

Automatically protect Github's default branch upon repository creation and creates an issue informing users what protections have been automatically set. This is useful for GitHub administrators looking to enforce specific repository protections for their teams and users while providing sensible defaults for organizational governance.

For more details on available settings see [Github API v3 documentation - Update branch protection](https://developer.github.com/v3/repos/branches/?#update-branch-protection)

## Google Cloud Function

This is a serverless webhook function. The service performs the following operations:

* listens for repository events from a GitHub webhook
* when the `{"action": "created"}` key is present in the github response, apply branch protections as outlined in `config.json`. 
* notify the repository creator of protections that have been applied

## Getting Started
### Requirements
#### Google Cloud Platform:
1. Access to Google Cloud Platform
2. Access to the GCP console and or gcloud CLI
3. Access to create a serviceaccount
4. Access to create a secret and apply permissions with IAM to the secret/serviceaccount
5. Mirror a GitHub repo with Google Cloud Source
6. The ability to create a Google Cloud Function
#### GitHub:
1. Github Organization
2. API Access, token generation
3. Webhook configuration
4. Create repository secrets
5. GitHub Actions for Build and Deploy


### Setup

1. [Creating a personal access token for the command line](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
    * limit the scope to repo
  
2. Enable secret manager and cloud functions on Google Cloud Platform
     * ```sh
       $ gcloud services enable secretmanager.googleapis.com cloudfunctions.googleapis.com
       ```
3. Add your Github personal access token to Google secrets manager (replace `<GITHUB_TOKEN>` with the key you created in step #1). We will use this token to apply branch protections and create issues.
     * ```sh
       $ echo -n <GITHUB_TOKEN> | \
         gcloud beta secrets create github-branch-protect \
         --data-file=- \
         --replication-policy automatic
       ```
4. Grant access to the secret with a serviceaccount (replace `<GCP_PROJECT>` with your Google Cloud Platform project name)
    * ```sh
      gcloud beta secrets add-iam-policy-binding github-branch-protect \
        --role roles/secretmanager.secretAccessor \
        --member serviceAccount:<GCP_PROJECT>@appspot.gserviceaccount.com
      ```
5. Clone this repo into your organization

6. [Mirror the cloned repo with Google Cloud Source Repositories](https://cloud.google.com/source-repositories/docs/mirroring-a-github-repository). This will enable the ability to deploy using GitHub Actions upon success build and test.

7. Create a Google Cloud Function (update `--project`, `--region`, `--service-account`, and `--source` to match your settings)
    * ```sh
      gcloud functions deploy github-branch-protecth \
        --project=github-branch-protect \
        --region=us-central1 \
        --runtime=python37 \
        --service-account=github-branch-protect@appspot.gserviceaccount.com \
        --source=https://source.developers.google.com/projects/github-branch-protect/repos/github_paper-street-soap-co_github-branch-protect/moveable-aliases/master/paths// \
        --entry-point=repository_event_http
      ```
8. [Create a webhook](https://developer.github.com/webhooks/creating/) in Github with the URL from your Google Cloud Function
    * Set the payload URL
        * ```
          https://<REGION>-<PROJECT>.cloudfunctions.net/<GOOGLE_CLOUD_FUNCTION>
          https://us-central1-github-branch-protect.cloudfunctions.net/github-branch-protect 
          ```
    * Set Content type to `application/json`
    * Select "Let me select individual events.", set scope to `repository` only
  
### Deploy

Using Github Actions users can build, test, and deploy the microservice. This requires [repository secrets](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets) to be created. The workflow uses three secrets in total. Two for GCP and one for Coveralls.

* `COVERALLS_REPO_TOKEN`
    * The secret token for your repository, found at the bottom of your repository’s page on Coveralls
* `GCP_SA_EMAIL`
    * ```github-branch-protect@appspot.gserviceaccount.com```
* `GCP_SA_KEY`
    * [Creating and managing service account keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#iam-service-account-keys-create-console)
    * You can download a JSON key in the GCP console
    * Set the JSON contents as the secret in GitHub

The deploy job depends on the build/test job passing and the `master` branch

### Example Issue
You can see an example issue [here](https://github.com/Paper-Street-Soap-Co/github-branch-protect-example/issues/1) for the paper street soap co organization. The user is given an **@mention**, assigned, and given a detailed explanation of the protections and their settings with additional links to documentation if they'd like further details.




  


