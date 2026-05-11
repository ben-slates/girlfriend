
This guide is a strict step-by-step path for making `girlfriend` eventually installable like this:

```bash
sudo apt install girlfriend
```

on Debian, Ubuntu, and Kali with no custom repository setup by the user.

That only happens after the package is accepted into official repositories. So this guide focuses on the real A-to-Z process for getting there.

## Before You Start

You are working from this project:

```bash
/home/ben/Desktop/girlfriend
```

This guide assumes:

- you are on Debian or Ubuntu
- you have internet access
- you want the Debian-first route
- you want Ubuntu and Kali to become possible later through distro inclusion

## Step 1. Open the project directory

```bash
cd /home/ben/Desktop/girlfriend
```

Verify you are in the right place:

```bash
pwd
ls
```

You should see files like:

- `girlfriend/`
- `debian/`
- `README.md`
- `pyproject.toml`
- `setup.py`

## Step 2. Install Debian packaging tools

Run:

```bash
sudo apt update
sudo apt install -y build-essential devscripts debhelper-compat dh-python python3-all python3-setuptools python3-rich lintian debmake dh-make pbuilder sbuild piuparts fakeroot gnupg quilt pristine-tar autopkgtest
```

Wait for the installation to finish fully.

## Step 3. Review the current Debian packaging files

Open and inspect these files:

```bash
sed -n '1,200p' debian/control
sed -n '1,200p' debian/changelog
sed -n '1,200p' debian/rules
sed -n '1,200p' debian/copyright
sed -n '1,200p' debian/install
cat debian/source/format
```

Check these points:

- package name is `girlfriend`
- distribution in changelog is `unstable`
- package description is professional enough
- runtime dependency includes `python3-rich`
- optional tools are not hard dependencies

If `debian/changelog` does not use `unstable`, fix it before continuing.

## Step 4. Update `debian/changelog`

Edit `debian/changelog` so the first entry looks like this format:

```text
girlfriend (2.0.0-1) unstable; urgency=medium

  * Initial release.

 -- Your Name <you@example.com>  Sat, 09 May 2026 00:00:00 +0000
```

You can update it with:

```bash
dch --create -v 2.0.0-1 --package girlfriend
```

If the file already exists, use:

```bash
dch -i
```

Then open it and verify the top entry manually:

```bash
sed -n '1,20p' debian/changelog
```

## Step 5. Make sure dependencies are correct

Open:

```bash
sed -n '1,200p' debian/control
```

Make sure the binary package section contains the important runtime dependency:

```text
Depends: ${misc:Depends}, ${python3:Depends}, python3-rich
```

And recommended packages:

```text
Recommends: espeak-ng | espeak, libnotify-bin | notify-osd
```

If this is wrong, edit `debian/control` before going forward.

## Step 6. Build the binary package locally

From the project root run:

```bash
dpkg-buildpackage -us -uc -b
```

This should create files in the parent directory.

Check them:

```bash
cd ..
ls -la girlfriend_*
```

You should see files like:

- `girlfriend_2.0.0-1_all.deb`
- `girlfriend_2.0.0-1_amd64.buildinfo`
- `girlfriend_2.0.0-1_amd64.changes`

Then go back:

```bash
cd /home/ben/Desktop/girlfriend
```

## Step 7. Install the package locally and test it

From the parent directory:

```bash
cd ..
sudo dpkg -i girlfriend_2.0.0-1_all.deb
sudo apt -f install
```

Now test the installed command:

```bash
girlfriend --help
girlfriend --version
girlfriend
girlfriend compliment
girlfriend roast
girlfriend monitor
girlfriend config
```

If voice support is installed, also test:

```bash
girlfriend speak
```

If notifications are installed, also test:

```bash
girlfriend notify-test
```

If anything fails, stop and fix it before continuing.

## Step 8. Remove the installed package after testing

Clean the system package state:

```bash
sudo apt remove -y girlfriend
```

Then return to the project directory:

```bash
cd /home/ben/Desktop/girlfriend
```

## Step 9. Run the Python tests

Run:

```bash
python3 -m unittest discover -s tests -v
```

Make sure all tests pass.

Do not continue until the test output ends with:

```text
OK
```

## Step 10. Run `lintian`

Move to the parent directory:

```bash
cd ..
```

Run:

```bash
lintian -i -I --pedantic girlfriend_2.0.0-1_all.deb
```

Also run:

```bash
lintian -i -I --pedantic girlfriend_2.0.0-1_amd64.changes
```

Read every error and warning carefully.

Fix serious issues before continuing.

Then return:

```bash
cd /home/ben/Desktop/girlfriend
```

## Step 11. Add a manual page

Official Debian packaging is stronger if the CLI has a man page.

Create:

```text
debian/girlfriend.1
```

The man page should describe:

- command name
- synopsis
- description
- commands
- options
- config directory
- examples

After creating it, verify it exists:

```bash
ls -la debian/girlfriend.1
```

## Step 12. Add Debian autopkgtests

Create this directory if it does not already exist:

```bash
mkdir -p debian/tests
```

Create:

```text
debian/tests/control
debian/tests/smoke
```

The smoke test should at minimum verify:

```bash
girlfriend --help
girlfriend --version
```

Make the smoke script executable:

```bash
chmod +x debian/tests/smoke
```

Verify:

```bash
ls -la debian/tests
```

## Step 13. Rebuild the package after adding the man page and tests

Run:

```bash
dpkg-buildpackage -us -uc -b
```

This ensures the packaging still builds after your Debian-specific additions.

## Step 14. Create the upstream orig tarball

Go to the parent directory:

```bash
cd /home/ben/Desktop
```

Create the upstream tarball:

```bash
tar --exclude='./girlfriend/.git' --exclude='./girlfriend/.venv' --exclude='./girlfriend/__pycache__' --exclude='./girlfriend/.pytest_cache' -czf girlfriend_2.0.0.orig.tar.gz girlfriend
```

Check it exists:

```bash
ls -la girlfriend_2.0.0.orig.tar.gz
```

Go back:

```bash
cd /home/ben/Desktop/girlfriend
```

## Step 15. Build the source package

Run:

```bash
debuild -S -sa
```

This creates the source package files needed for Debian sponsorship.

Check the parent directory:

```bash
cd ..
ls -la girlfriend_2.0.0-1_source.changes girlfriend_2.0.0-1.dsc girlfriend_2.0.0.orig.tar.gz
```

Then return:

```bash
cd /home/ben/Desktop/girlfriend
```

## Step 16. Create a GPG key for Debian packaging work

If you do not already have a suitable GPG key, create one:

```bash
gpg --full-generate-key
```

Choose:

- RSA and RSA
- 4096 bits
- your real name
- your real email

Then list your key:

```bash
gpg --list-secret-keys --keyid-format LONG
```

Export your public key:

```bash
gpg --armor --export YOURKEYID > ~/publickey.asc
```

## Step 17. Build the signed source package

From the project directory:

```bash
debuild -S -sa
```

If signing is correctly set up, the resulting source package should be signed automatically.

Check the output files:

```bash
cd ..
ls -la girlfriend_2.0.0-1_source.changes girlfriend_2.0.0-1.dsc
```

## Step 18. Test in a clean build environment

This is important because Debian reviewers care about undeclared dependencies.

Run a clean build with `pdebuild`:

```bash
cd /home/ben/Desktop/girlfriend
pdebuild
```

If you use `sbuild`, run:

```bash
sbuild
```

If the clean build fails, fix the packaging and repeat this step.

## Step 19. Test install and removal with `piuparts`

Go to the parent directory:

```bash
cd ..
```

Run:

```bash
piuparts girlfriend_2.0.0-1_all.deb
```

This checks:

- install works
- remove works
- package cleanup is sane

If this fails, fix the package and rerun.

## Step 20. Create Debian account infrastructure

Create these accounts:

1. Debian Salsa account
2. Debian Mentors account

You will need them for collaborative packaging and sponsorship.

After creating them:

- upload your GPG public key where required
- confirm email addresses
- set up your maintainer identity

## Step 21. Prepare the source package for Mentors

From the parent directory verify these files exist:

```bash
cd /home/ben/Desktop
ls -la girlfriend_2.0.0-1_source.changes girlfriend_2.0.0-1.dsc girlfriend_2.0.0.orig.tar.gz
```

These are the important upload artifacts.

## Step 22. Upload to Debian Mentors

Install `dput` if needed:

```bash
sudo apt install -y dput
```

Upload:

```bash
dput mentors girlfriend_2.0.0-1_source.changes
```

Wait for the upload to complete.

Then open the Debian Mentors package page and verify the upload is visible.

## Step 23. Publish the packaging repository

Make sure your source repository is public and clean.

It should contain:

- source code
- Debian packaging files
- tests
- documentation

Avoid junk files like:

- local virtual environments
- build output
- editor temp files

If needed, clean the repository before requesting sponsorship.

## Step 24. Request Debian sponsorship

Prepare a sponsorship request that includes:

- package name: `girlfriend`
- short explanation of what it does
- link to Mentors upload
- link to source repository
- note that `lintian` was run
- note that clean builds were tested
- note that local install testing was completed

Then post your request through the appropriate Debian sponsorship channel.

## Step 25. Respond to review feedback

A Debian sponsor will likely request changes.

Typical changes include:

- better long description
- man page improvements
- copyright corrections
- dependency cleanup
- policy compliance fixes
- test improvements

When feedback arrives:

1. edit the package
2. update `debian/changelog`
3. rebuild source package
4. rerun `lintian`
5. reupload

Repeat until the sponsor is satisfied.

## Step 26. Wait for Debian acceptance

Once a sponsor uploads your package to Debian, it will go through Debian archive processing.

If accepted, it becomes part of Debian.

At that stage Debian users can eventually install it through:

```bash
sudo apt update
sudo apt install girlfriend
```

## Step 27. Track Ubuntu inclusion

After Debian acceptance, watch whether Ubuntu syncs the package during development cycles.

If Ubuntu syncs it, Ubuntu users can eventually install it with:

```bash
sudo apt update
sudo apt install girlfriend
```

If Ubuntu does not sync it automatically, separate Ubuntu packaging work may be needed later.

## Step 28. Track Kali inclusion

After Debian acceptance, check whether Kali imports it or is willing to package it.

Kali is selective, so acceptance is not guaranteed.

But Debian acceptance gives you the strongest possible starting point.

## Step 29. Release updates properly

For every new version:

1. update your Python package version
2. update `debian/changelog`
3. rebuild binary package
4. rerun tests
5. rerun `lintian`
6. rebuild source package
7. upload new source package

Typical update commands:

```bash
cd /home/ben/Desktop/girlfriend
dch -i
dpkg-buildpackage -us -uc -b
debuild -S -sa
cd ..
lintian -i -I --pedantic girlfriend_*.changes
```

## Step 30. Understand the final result

If you complete the process successfully and the package is accepted by the distro, users will not need:

- custom APT repositories
- custom HTTPS package hosting
- manual GPG key install for your own repo

They will just do:

```bash
sudo apt update
sudo apt install girlfriend
```

That is exactly the outcome you asked for.

## Final Checklist

Do not submit until all of these are true:

- `dpkg-buildpackage -us -uc -b` works
- `debuild -S -sa` works
- `python3 -m unittest discover -s tests -v` passes
- local install with `dpkg -i` works
- `lintian` has no serious errors
- clean build in `pdebuild` or `sbuild` works
- `piuparts` works
- a man page exists
- Debian autopkgtests exist
- `debian/changelog` is correct
- `debian/control` dependencies are correct
- the source package uploads to Mentors successfully

Once all of that is done, the package is genuinely on the path toward becoming a real official APT package.
