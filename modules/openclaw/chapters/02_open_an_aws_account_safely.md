# Open an AWS account without living as the root user

An AWS account has one **root user**: the email address you sign up with. It can do everything,
including closing the account and changing payment details, and it cannot be restricted. The first
thing every AWS guide says, and the thing this chapter makes you do, is to lock the root user away
and create a second identity for daily work (diagram D58, left column).

## 1. Sign up

1. Go to [aws.amazon.com](https://aws.amazon.com) and choose **Create an AWS account**.
2. Enter an email address you control and an account name. Verify the email with the code sent.
3. Choose a strong root password. Store it in a password manager.
4. Contact details: choose **Personal**. Enter your address.
5. Payment: a card is required even on the Free plan. A small verification charge may appear and be
   reversed.
6. Phone verification: a code by SMS or call.
7. Choose the **Free plan** when offered. Since July 2025 new accounts choose between a Free plan
   and a Paid plan. The Free plan gives credits (100 US dollars at sign-up and up to 100 more for
   completing activities) that last six months or until spent, across most services, and cannot
   run up a bill beyond them. It is enough for this module many times over.
8. Support plan: **Basic** (free).

Sign in to the console as the root user once more to do the next two steps, then stop using it.

## 2. Protect the root user

1. In the console, open the account menu (top right) → **Security credentials**.
2. Under **Multi-factor authentication (MFA)**, **Assign MFA device**. Choose *Authenticator app*,
   scan the code with an app such as Google Authenticator, Microsoft Authenticator, Authy or 1Password,
   and enter two consecutive codes.
3. Do **not** create access keys for the root user. If the page shows any, delete them.

## 3. Create an administrator user for daily work

AWS offers two ways. The simpler one for a single person is an **IAM user**.

1. Search for **IAM** in the console search bar and open it.
2. **Users** → **Create user**. Name it, for example `admin`. Tick **Provide user access to the AWS
   Management Console**, choose *I want to create an IAM user*, set a password, and untick "must
   create a new password at next sign-in" if you prefer.
3. Permissions: **Attach policies directly** → tick **AdministratorAccess**. Next, **Create user**.
4. On the success page, note the **console sign-in URL**. It looks like
   `https://<account-id>.signin.aws.amazon.com/console`. Bookmark it.
5. Open the new user → **Security credentials** → **Assign MFA device** and enrol the authenticator
   app for this user too.
6. Sign out of the root user. Sign in at the bookmarked URL as `admin`. Everything from here on is
   done as this user.

Why this matters even for one person: a compromised IAM user can be deleted or restricted from the
root account; a compromised root user cannot. And you will one day paste a password somewhere you
should not.

If your organisation uses **IAM Identity Center** (single sign-on), use that instead; the outcome is
the same, an identity that is not root.

## 4. Set a budget alert

Credits or not, know when money moves.

1. Search for **Billing and Cost Management** → **Budgets** → **Create budget**.
2. Choose **Use a template** → **Zero spend budget** (alerts when any actual charge appears) and
   enter your email. Create it.
3. Optionally create a second one, **Monthly cost budget**, at 10 US dollars.

Also, in **Billing preferences**, tick the options to receive Free Tier usage alerts and PDF
invoices by email.

## 5. Choose a region

AWS is divided into regions (Frankfurt, Mumbai, Ohio, Sydney and so on). Resources live in one
region and the console shows one region at a time (the drop-down at the top right). Pick the one
nearest to you and stay in it for the whole module; a machine launched in one region is invisible
when the console is showing another. Write the region name down.

## What you have

- A root user with MFA that you no longer use.
- An `admin` IAM user with MFA and a bookmarked sign-in URL.
- A budget that emails you at the first cent, and a chosen region.

## Recap

- The root user is unrestricted and unrestrictable: give it MFA, no access keys, and stop using it.
- Do daily work as an IAM user (or an Identity Center user) with AdministratorAccess and MFA.
- Set a zero-spend budget alert and pick one region before creating anything.
