// __COMPDB_ENTRY: The contents of this compilation database entry.
// Should be a string literal.
// __COMPDB_SYMNAME: ATM I can't think of a way to generate a unique symbol
// name, so just force the TU to provide it.
__attribute__((section(".llvm.compdb")))
extern const char __COMPDB_SYMNAME[] = "<<<COMPDB:" __COMPDB_ENTRY ">>>";
