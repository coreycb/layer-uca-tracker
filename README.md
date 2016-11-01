# Overview

This charm tracks and publishes reports that compare Ubuntu Cloud Archive
package versions for OpenStack.  The charm generates an Nginx-based website
and publishes the reports to it.

There are two different version trackers:

* Base version tracker: Compares package versions from Ubuntu archives only.
* Upstream version tracker: Compares package versions from Ubuntu archives
  with the latest upstream versions.

# Usage

juju deploy cs:~corey.bryant/uca-tracker

juju config uca-tracker base-tracker-releases='ocata newton mitaka liberty'

juju config uca-tracker upstream-tracker-releases='ocata newton mitaka liberty'

Once deployed, a landing page with links to reports will be published to:
http://uca-tracker-ip

# Building

This is a layered charm.  If you intend to make changes to the charm it must
first be built with the `charm build` command before it can be used.
