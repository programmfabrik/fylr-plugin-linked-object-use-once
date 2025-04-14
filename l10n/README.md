# L10N Keys

## Error Messages

* `fylr-plugin-linked-object-use-once.error.duplicate_tan_object`:
    * Api error which is thrown when multiple objects link to the same TAN list object (in group edit mode)
    * Parameters:
        * `idx`: index of the main object in the list
        * `tan_objecttype`: objecttype of the linked TAN list object
        * `tan_obj_id`: object id of the linked TAN list object

* `fylr-plugin-linked-object-use-once.error.tan_object_already_linked`:
    * Api error which is thrown when a TAN list object is linked which is already linked in another object (single and group edit mode)
    * Parameters:
        * `idx`: index of the main object in the list
        * `tan_objecttype`: objecttype of the linked TAN list object
        * `tan_obj_id`: object id of the linked TAN list object

* `fylr-plugin-linked-object-use-once.error.could_not_load_tan_object`:
    * Api error which is thrown when the request to load the current version of a linked TAN list object failed
    * Parameters:
        * `idx`: index of the main object in the list
        * `tan_objecttype`: objecttype of the linked TAN list object
        * `tan_obj_id`: object id of the linked TAN list object
        * `msg`: generic error message
        * `statuscode`: HTTP status code
        * `response`: response text to the request

* `fylr-plugin-linked-object-use-once.error.could_not_update_tan_object`:
    * Api error which is thrown when the request to update the updated version of a linked TAN list object failed
    * Parameters:
        * `idx`: index of the main object in the list
        * `tan_objecttype`: objecttype of the linked TAN list object
        * `tan_obj_id`: object id of the linked TAN list object
        * `msg`: generic error message
        * `statuscode`: HTTP status code
        * `response`: response text to the request
