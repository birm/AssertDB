import os
import smtplib
import email
import time
import sqlalchemy

class Assertion(object):
    """Check an assumption against a db.
        args:
            assertions: list of lists, where each element
                        is a list with this structure:
                select
                uri (e.g. mysql://localhost/myschema)
                table
                comparision (eq, gt, lt, ne)
                target (value to compare against)
                where logic
            email: an address to send exceptions to.
                if email is blank/unset, then it returns the results."""

    def __init__(self, assertions=[["count(*)", "mysql://localhost/mysql",
                                    "user", "ne", 0, "TRUE"]],
                 email=""):
        """create assertion object."""
        self.assertions = assertions
        # check if assertions is a file
        # if so read it
        # if not, continue and hope it's a properly formatted list
        self.email = email

    def _fromfile(self):
        """
        Get the assertion infrormation from a simple file.
        Format:
        {uri} {table} {select} {where} {comparision} {target}
        SAMPLE:
        mysql://localhost/mysql user count(*) user="bob" gt 0
        mysql://localhost/information_schema tables sum(DATA_FREE) lt 100000
        """
        pass


    def _compare(self, result, target, comparison):
        """
        Perform a comparison per specifications.
        Returns a boolean with the result of the comparison.
        """
        if comparison == "ne":
            return not result == target
        if comparison == "eq":
            return result == target
        if comparison == "gt":
            return float(result) > float(target)
        if comparison == "lt":
            return float(result) < float(target)
        else:
            raise ValueError("Invalid comparison operator " + comparison)

    def _fails(self, select, uri, table, comparison, target, where):
        """
        Check if the conditions are met.
        Return False if OK, True if issue.
        """
        db = sqlalchemy.create_engine(uri)
        query = "select {0} from {1} where {2}".format(select, table, where)
        result = db.engine.execute(query)
        if self._compare(result, target, comparison):
            return False
        else:
            return result

    def _notify(self, result, args):
        """
        Send an email to notify with results, or return the result.
        """
        if email == "":
            print(result)
        else:
            msg = email.mime.text.MimeText(repr(args) + " got " + result)
            msg['Subject'] = "[AssertDB] failed on " + args[1] + "." + args[2]
            msg['To'] = self.email
            try:
                smtp = smtplib.SMTP("localhost")
                smtp.sendmail(self.email, msg.as_string())
            except:
                raise RuntimeError("Email send failed.")

    def check(self):
        """
        Check each assertion given.
        Returns nothing, but sends emails with assertions.
        """
        for x in self.assertions:
            result = self._fails(*x)
            if result:
                self.notify(result, x)

if __name__ == "__main__":
    # run for single check from cli
    import sys
    args = ["count(*)", "mysql://localhost/mysql" "user", "ne", 0, "TRUE", ""]
    for x in range(0, len(sys.argv)-1):
        args[x] = sys.argv[x]
    searcher = Assertion([args[:-1]], args[-1])
    searcher.check()
    if email != "":
        print("Completed the checks; check email for result")
