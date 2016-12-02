import os
import smtplib
import email
import time

class Assertion(object):
    """Check an assumption against a db.
        args:
            assertions: list of lists, where each element
                        is a list with this structure:
                select
                host
                db.table
                comparision (eq, gt, lt, ne)
                target (value to compare against)
                where logic
            email: an address to send exceptions to.
                if email is blank, then it returns the results."""

    def __init__(self, assertions=[["count(*)", "localhost", "mysql.user",
                                    "ne", 0, "TRUE"]], email="root@localhost"):
        """create assertion object."""
        self.assertions = assertions
        self.email = email

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
        if comparison == "gt":
            return float(result) < float(target)
        else:
            raise ValueError("Invalid comparison operator " + comparison)

    def _fails(self, select, host, table, comparison, target, where):
        """
        Check if the conditions are met.
        Return False if OK, True if issue.
        """
        if host == "localhost":
            command = """mysql -N "select {0} from {1} where {2}" \
            | awk '{print $1}'""".format(select, table, where)
        else:
            command = """mysql -N -h {3} "select {0} from {1} where {2}" \
            | awk '{print $1}'""".format(select, table, where, host)
        result = os.system(command)
        if self._compare(result, target, comparison):
            return False
        else:
            return result

    def _notify(self, result, args):
        """
        Send an email to notify with results.
        """
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
    args = ['root@localhost', "count(*)", "mysql.user", "ne", 0, "TRUE"]
    for x in range(0, len(sys.argv)-1):
        args[x] = sys.argv[x]
    searcher = AssertDB(args[0], [args[1:]])
    searcher.check()
    print("Completed the expansion; check files for result")
