# License OPL-1 (See LICENSE file for full copyright and licensing details).

=================
Credit Management
=================

Configuration
=============
* Add Prepayment Test can be enabled from Sales configuration
Sales -> Settings -> Enable "Add Prepayment Test" to test even if credit limit is equal to 0.

Fields
=======
* Total Credit Used = Total Receivable + The amount of Sale Orders confirmed but not yet invoiced + The invoices that are in draft state.
* Credit Hold = Boolean field(True/False)
 
Functionality
==============
If Credit Hold field is True

In Sales
---------
* While choosing the customer in a sales order a warning message is displayed.  The user will not be able to confirm the sales order.

In Delivery Order
------------------
* The user will not be able to confirm the delivery order or to "Mark As Todo", "Check Availability", "Recheck Availablity", "Force Availability" and "validate".

If Credit Limit is not zero.

In Sales
---------
* If "Total Credit Used" is greater than or equal to "Credit Limit", in sales order a warning message is displayed when the customer is selected.  The user is not able to confirm the sales order.
* If the Total Credit Used + sales order amount exceed the credit limit then the user is not allowed to confirm the sales order.
* There is no constraint on the DO based on the credit limit.,
        
Credits
========

Contributors
------------
* Sodexis <dev@sodexis.com>

This module is maintained by Sodexis.
