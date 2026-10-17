#include <windows.h>
#include <dia2.h>
#include <cstdio>
#include <set>
#include <string>

// 只读部署 PDB 的源码校验和；不注册 COM，也不修改 PDB 或源码。
int wmain(int argc, wchar_t** argv) {
    if (argc != 3) return 2;
    if (FAILED(CoInitialize(nullptr))) return 3;
    auto dll = LoadLibraryW(argv[1]);
    if (!dll) return 4;
    using GetFactory = HRESULT (WINAPI*)(REFCLSID, REFIID, LPVOID*);
    auto getFactory = reinterpret_cast<GetFactory>(GetProcAddress(dll, "DllGetClassObject"));
    if (!getFactory) return 5;
    IClassFactory* factory = nullptr;
    if (FAILED(getFactory(__uuidof(DiaSource), IID_IClassFactory, reinterpret_cast<void**>(&factory)))) return 6;
    IDiaDataSource* source = nullptr;
    auto result = factory->CreateInstance(nullptr, __uuidof(IDiaDataSource), reinterpret_cast<void**>(&source));
    factory->Release();
    if (FAILED(result)) return 7;
    if (FAILED(source->loadDataFromPdb(argv[2]))) return 8;
    IDiaSession* session = nullptr;
    if (FAILED(source->openSession(&session))) return 9;
    IDiaSymbol* global = nullptr;
    if (FAILED(session->get_globalScope(&global))) return 10;
    IDiaEnumSymbols* compilands = nullptr;
    if (FAILED(global->findChildren(SymTagCompiland, nullptr, nsNone, &compilands))) return 11;
    IDiaSymbol* compiland = nullptr;
    ULONG count = 0;
    std::set<std::wstring> emitted;
    while (compilands->Next(1, &compiland, &count) == S_OK && count == 1) {
        IDiaEnumSourceFiles* files = nullptr;
        if (SUCCEEDED(session->findFile(compiland, nullptr, nsNone, &files))) {
            IDiaSourceFile* file = nullptr;
            while (files->Next(1, &file, &count) == S_OK && count == 1) {
                BSTR name = nullptr;
                BYTE digest[256]{};
                DWORD length = 0, type = 0;
                if (file->get_fileName(&name) == S_OK && file->get_checksumType(&type) == S_OK &&
                    file->get_checksum(sizeof(digest), &length, digest) == S_OK) {
                    std::wstring key(name);
                    key += L"|" + std::to_wstring(type) + L"|";
                    wchar_t hex[3]{};
                    for (DWORD index = 0; index < length; ++index) {
                        swprintf_s(hex, L"%02x", digest[index]); key += hex;
                    }
                    if (emitted.insert(key).second) wprintf(L"%s\n", key.c_str());
                }
                SysFreeString(name);
                file->Release();
            }
            files->Release();
        }
        compiland->Release();
    }
    compilands->Release(); global->Release(); session->Release(); source->Release();
    FreeLibrary(dll); CoUninitialize();
    return 0;
}
