# What is it?

This is a quick prototype exploring the viability of embedding Clang
[compilation database](http://clang.llvm.org/docs/JSONCompilationDatabase.html)
information inside the emitted object file.

Note that this prototype uses `readelf` and moreover it uses a rather obscure
(but super useful) option `--string-dump=<section number or name>`, so it may
not have an equivalent on your system. As such, here is a demo of it running:

```
sean:~/pg/CompilationDatabase % ninja -v
[3/1/0] ./compdb_inserter.py -c Foo.cpp -o Foo.o
[2/2/0] ./compdb_inserter.py -c Bar.cpp -o Bar.o
[1/1/2] ./compdb_inserter.py -o Game Foo.o Bar.o
[0/1/3] readelf --string-dump=.clang.compdb Game | sed --quiet 's/^.*<<<COMPDB:\(.*\)>>>.*$/\1/p' | ./lines2jsonarray.py > compdb.json
sean:~/pg/CompilationDatabase % cat compdb.json
[
{"directory": "/home/sean/pg/CompilationDatabase", "command": "clang++ -c Foo.cpp -o Foo.o", "file": "Foo.cpp"}

,
{"directory": "/home/sean/pg/CompilationDatabase", "command": "clang++ -c Bar.cpp -o Bar.o", "file": "Bar.cpp"}

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
