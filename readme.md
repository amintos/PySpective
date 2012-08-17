PySpective
==========

An idea for a Python BDD-style spec runner inspired by *rspec*.

Example
-------
```python
# the unit under test

def factorial(n):
    if n < 0:
        raise ValueError, "n must be non-negative"
    else:
        return n * factorial(n - 1) if n else 1
```
```python
# the spec

from spec import describe, done

with describe("The factorial function") as it:

    with it("is defined at zero") as then:
        then(factorial(0)).should.be(1)

    with it("rejects a negative argument") as then:
        then(lambda: factorial(-1)).should.throw(ValueError)

    with it("yields 720 if input is 6") as then:
        then(factorial(6)).should.be(720)

    with it("grows fast") as then:
        then(factorial(100)).should > 100000
		
done()
#  ^ don't forget!
```

Just run this with python and you will get the following output. Try to break a test case and re-run.
```
The factorial function
   is defined at zero.
   rejects a negative argument.
   yields 720 if input is 6.
   grows fast.
4 of 4 assertions passed.
```

More Examples
-------------

Types of **Expectations**:

```python
with describe("A Feature") as it:
	with it("behaves this way") as then:
	
		# should_not for denying any expectation:
		
		then('abc').should_not.be('ABC')
		then(lambda: 42 / 7).should_not.throw(ZeroDivisionError)
```

```python
		# Comparison operators:
		
		then(42).should > 23
		then(42).should < 666
		then(42).should >= 42
		then(42).should <= 42
```

```python
		# Boolean statements
		
		then(isinstance(42, int)).should.hold()
```

```python
		# Duck Typing
		
		then('a string').should.have('join')		
```

```python
		# Collection checking
		
		then([1, 2, 3]).should.contain(1)
```

```python
		# Expecting exceptions
		
		then(lambda: 1 / 0).should.throw(ZeroDivisionError)
```

```python
		# RegEx matching
		
		then("a string").should.match("^a")
```

**Finalizing** the test run:

<code>done()</code> prints the test summary and exits the interpreter returning the number of failed expectations as exit code.

<code>done(exit=False)</code> also prints the summary but does not exit. Anyhow, it resets the result collector including the counters for failed and succeeded tests.

The Meta-Spec
-------------

<code>spec_spec.py</code> contains the tests for the test runner itself. It uses all features of the spec framework itself including custom expectations/assertions and a mocked result collector.

