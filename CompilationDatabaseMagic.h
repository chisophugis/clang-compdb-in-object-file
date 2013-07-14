// The following macros should be defined on entry to this file:
// __COMPDB_ENTRY:
//   The contents of this compilation database entry. Should be a string
//   literal.
// __COMPDB_SYMNAME:
//   ATM I can't think of a way to generate a unique symbol name, so just
//   force it to be passed in.
__attribute__((section(".clang.compdb")))
extern const char __COMPDB_SYMNAME[] = "<<<COMPDB:" __COMPDB_ENTRY ">>>";
