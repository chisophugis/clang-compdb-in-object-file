# What is it?

This is a quick prototype exploring the viability of embedding Clang
[compilation database](http://clang.llvm.org/docs/JSONCompilationDatabase.html)
information inside the emitted object file.

Experience note: I have used a this approach at work to extract compilation
databases from projects with extremely unfriendly build systems. It works
like a charm. Also, see my note below about a "better format", which really
makes everything simpler and easier.

Note that this prototype uses `readelf` and moreover it uses a rather obscure
(but super useful) option `--string-dump=<section number or name>`, so it may
not have an equivalent on your system. As such, here is a demo of it running:

```
sean:~/pg/clang-compdb-in-object-file % ninja -v
[3/1/0] ./compdb_inserter.py -c Foo.cpp -o Foo.o
[2/2/0] ./compdb_inserter.py -c Bar.cpp -o Bar.o
[1/1/2] ./compdb_inserter.py -o Game Foo.o Bar.o
[0/1/3] readelf --string-dump=.clang.compdb Game | sed --quiet 's/^.*<<<COMPDB:\(.*\)>>>.*$/\1/p' | ./lines2jsonarray.py > compile_commands.json
sean:~/pg/clang-compdb-in-object-file % cat compile_commands.json
[
{"directory": "/home/sean/pg/clang-compdb-in-object-file", "command": "clang++ -c Foo.cpp -o Foo.o", "file": "Foo.cpp"}

,
{"directory": "/home/sean/pg/clang-compdb-in-object-file", "command": "clang++ -c Bar.cpp -o Bar.o", "file": "Bar.cpp"}

]
```

# How does it work?

Basically, it embeds the compilation database entry for the file inside a
special `.clang.compdb` section, which is then merged by the linker. The
"proper" way to do this would be for clang to add this information, but for
this prototype, I made a compiler wrapper script `./compdb_inserter.py`
which just passes through to clang, but adds some commandline options which
cause the `.clang.compdb` section to be created with the right contents.
For now, it adds:

- `-include CompilationDatabaseMagic.h`: this causes clang to include the
  `CompilationDatabaseMagic.h` file before parsing the file, this file in
  turn will use the two other options to add the compilation database entry
  to the `.clang.compdb` section.
- `-D__COMPDB_ENTRY="{\"directory\":...,\"command\":...,\"file\":...}"`:
  defines this macro to be a string literal containing the compilation
  database entry.
- `-D__COMPDB_SYMNAME=...`: see CompilationDatabaseMagic.h for why this is
  currently needed.

# How did you think of this?

The inspiration came from [this comment](http://eli.thegreenplace.net/2012/01/06/pyelftools-python-library-for-parsing-elf-and-dwarf/#comment-833399)
on Eli Bendersky's blog.

# You know you could have ...

Yes, I'm aware how ironic it is that I'm using ninja, and not just doing
`ninja -t compdb cxx`. I'm primarily using ninja for automation here, and not
as a "build system" per se. This approach of embedding compilation database
info is intended to work with *arbitrary* build systems, as it would eventually
be inserted by the compiler.

# Can we make this simpler/easier/more robust/more flexible?

A better format for embedding this information (rather than just the JSON)
makes it trivially easy to extract without any specialized tools or a
special object file section; you can get by with just a regex and no
knowledge of the file format.

For example, consider embedding the compilation database info as
`@<md5>:<length>:<JSON>`, where the `<md5>` is a hash of the entire
string (with the hash itself replaced with 0's, or omitted, or whatever).
Searching for the regex `@[0-9a-f]{32}:[0-9]+:` in the raw file will find
all potential embedded JSON strings with a very low false positive rate;
the hash can then be checked to avoid false positives.

You can also do `@<md5>:<length>:<metadata>:<JSON>` to get some useful
side-channel information.  E.g. `<metadata>` could be a unique identifier
generated for a particular build, so that you can avoid any other embedded
compilation database information. I suppose you could put this metadata
directly in the JSON too (might be easier to process that way). Another
possibility is to put a timestamp so that you can filter based on when the
code was compiled, or a git commit hash to know what was being compiled to
generate this, etc.

Such a format allows casting a very "wide net" to find all possible
compilation database entries; usually all build products are known to lie
below a particular working directory, so just scan *all* files below that
directory. Certain very hostile build systems may require something this
flexible. This scan is basically a "grep" operation and can be made
extremely fast. On the other hand, it's extremely simple, and a working,
probably-fast-enough first implemetation can be done in less than an hour
with a short Python script, which can then be iterated on and easily
customized (all the expensive operations (regex, md5) have optimized
implementations in the stdlib).

Remember, all of this depends on being able to ensure that a particular
byte sequence (the special string) is preserved verbatim across the build
process and into the output. String literals are an obvious way to
accomplish this; i.e. if you print a string literal in your program, you
can be pretty darn sure that your output program will contain the string no
matter what build steps happen. However, any other mechanism for
getting a sequence of bytes preserved across the build process and into the
final build products would work as well. If you're desperate, you could
even scan the running program's address space right before shutdown in
order to catch things from e.g. shared libraries.

# Any future directions?

In general, it seems like a good idea for every step of the build pipeline
to have the option of recording the information needed to reproduce that
step, since then by just enabling the option on all your tools you can
create a reproducible record of your build.

I think that it would be nice to have some standardized format for tools to
share this information. It would need to be more sophisticated than clang's
compilation database, since you would really want it to communicate the
needed ingredients for exactly reproducing a build step. For example, it
should be possible to feed all these tool "repro records" to a program,
which then is able to output a convenient package of everything needed to
reproduce the build.
