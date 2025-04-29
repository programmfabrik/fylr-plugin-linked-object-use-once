# fylr-plugin-linked-object-use-once

This plugin provides the possibity to allow the linking of specific objects only once. If another object tries to link to these objects, an api error is thrown. This can be used to identify objects with a unique linked object.

These linked objects can be used to allow identifiers from a unique, prepared list of values. This gives the possibility to use lists of objects with prefilled values like values from a TAN list. To identify an object as "assigned", tags are used.

These linked objects will be called "TAN (list) objects" here, the objects which link to these objects will be called "main objects".

Objects and Tags are configured in the base configuration (see below).


## Installation

In fylr, open the Plugin Manager, and add a new plugin with type `url`, and enter the URL:

[`https://github.com/programmfabrik/fylr-plugin-linked-object-use-once/releases/latest/download/fylr-plugin-linked-object-use-once.zip`](https://github.com/programmfabrik/fylr-plugin-linked-object-use-once/releases/latest/download/fylr-plugin-linked-object-use-once.zip)

This URL always links to the ZIP file of the latest release, so it is updated automatically after a new version has been released.


## Key Features

* The Plugin checks if a new or updated object contains any linked TAN list object which was not linked before
* If a TAN object is linked, its tag is checked:
    * If it is "free", the tag is changed to "assigned" and the TAN object and main object are updated
    * If it is "assigned", an api error is thrown (see below)


## Requirements


### Datamodel


#### TAN (list) objects

Must be designed in the datamodel so that they fulfill these mandatory requirements:

* Tag management: to mark a TAN object as "free" or "assigned", the objecttype **must** have tags
* A text/string field which saves the identifier

Further optional objecttype settings, which are not enforced but strongly **recommended**, are:

* The identifier text/string field should have a `UNIQUE` constraint
* The identifier text/string field should have a `NOT NULL` constraint


#### Main objects

These objects need at least one link to one of the TAN list objects.


### Rights management

The plugin uses the fylr API with the same access token as the user who saved the objects.

Additionaly to the write- and read rights, which are required to update the main object and link a TAN list object, the user also needs write and mask rights on the TAN list objecttype. This is needed to change the tag in the linked TAN list object.


## Configuration

The plugin is configured in the base configuration under "Plugins" -> "fylr-plugin-linked-object-use-once".

Under "TAN Settings", multiple entries can be added to the table "Relations between main objecttypes and TAN list objects". Each entry has these following mandatory fields:

* TAN list objecttype:
    * Select one of the objecttypes to use for TAN list objects
    * Only objecttypes with tag management are available
    * It must be linked in the main objecttype
* Main objecttype:
    * Main objecttype which links to the TAN list objecttype
* Tag "free":
    * Tag which indicates that a TAN list object is still free and can be assigned
    * The plugin checks if a newly linked TAN object has this tag
    * After saving, this tag will be removed from the linked TAN list object
* Tag "assigned":
    * Tag which indicates that a TAN list object is already assigned and can not be linked
    * The plugin checks if a newly linked TAN object does not have this tag
    * After saving, this tag will be added to the linked TAN list object


## Usage

The Plugin is triggered after objects are saved in the editor. If all newly linked TAN list object(s) are "free" (defined by their tag), then the object is saved without any further information. The linked TAN list object(s) are updated, the tag for each object is changed from "free" to "assigned".

If any of the linked TAN objects already has a tag "assigned", an api error is thrown and displayed in the frontend. Saving the object is not possible in this state. Another free TAN object must be selected and the object must be saved again.

**Important:** Using the group editor to link TAN list objects is not possible! Assigning the same TAN object to more than one object is not allowed. This means that the group editor can only be used to change other fields which are not related to the TAN list objects.


## Error Messages

See also: [detailed l10n keys](l10n/README.md)

#### `fylr-plugin-linked-object-use-once.error.duplicate_tan_object`

Api error which is thrown when multiple objects link to the same TAN list object. It indicates that objects are updated in the group edit mode, and TAN list objects are linked, which is not allowed.

#### `fylr-plugin-linked-object-use-once.error.tan_object_already_linked`

Api error which is thrown when a TAN list object is linked, which is already linked in another object (single and group edit mode).

#### `fylr-plugin-linked-object-use-once.error.could_not_load_tan_object`

Api error which is thrown when the request to load the current version of a linked TAN list object failed. It contains the response to determine the actual error.

#### `fylr-plugin-linked-object-use-once.error.could_not_update_tan_object`

Api error which is thrown when the request to update the updated version of a linked TAN list object failed. It contains the response to determine the actual error.

