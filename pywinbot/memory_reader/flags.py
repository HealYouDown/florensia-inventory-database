# https://docs.microsoft.com/de-de/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot
TH32CS_INHERIT = 0x80000000
TH32CS_SNAPHEAPLIST = 0x00000001
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
TH32CS_SNAPPROCESS = 0x00000002
TH32CS_SNAPTHREAD = 0x00000004
TH32CS_SNAPALL = (TH32CS_SNAPHEAPLIST | TH32CS_SNAPMODULE |
                  TH32CS_SNAPPROCESS | TH32CS_SNAPTHREAD)

# https://docs.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
