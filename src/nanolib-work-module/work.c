#define PY_SSIZE_T_CLEAN 1
#include "Python.h"

#include "blake2.h"

#include <stdint.h>
#include <stdio.h>

#define HASH_BYTES 32
#define ITERATION_COUNT 250000


uint64_t do_work(const uint8_t block_hash[HASH_BYTES], const uint64_t nonce, const uint64_t threshold) {
    uint64_t work = nonce;
    uint64_t result = 0;

    blake2b_state hash;
    blake2b_init(&hash, sizeof(result));

    uint32_t iterations = ITERATION_COUNT;

    while (iterations > 0 && result < threshold) {
        work++;

        blake2b_update(&hash, &work, sizeof(work));
        blake2b_update(&hash, block_hash, HASH_BYTES);
        blake2b_final(&hash, &result, sizeof(result));
        blake2b_init(&hash, sizeof(result));

        iterations--;
    }

    return work;
}

PyDoc_STRVAR(work_do_work_doc,
"do_work(block_hash, nonce, threshold)\n\
\n\
Perform work on a block PoW. Return a positive 64-bit nonce if a match was found,\n\
otherwise return 0.");

static PyObject *
work_do_work(PyObject *self, PyObject *args)
{
    const uint8_t *block_hash;
    Py_ssize_t block_hash_size;
    uint64_t nonce;
    uint64_t threshold;

    if (!PyArg_ParseTuple(args, "y#KK",
                          &block_hash, &block_hash_size, &nonce, &threshold)) {
        return NULL;
    }

    if (block_hash_size != HASH_BYTES) {
        PyErr_SetString(PyExc_TypeError,
                        "'block_hash' needs to have a size of exactly 32 bytes");
        return NULL;
    }

    uint64_t result = 0;
    Py_BEGIN_ALLOW_THREADS
    result = do_work(block_hash, nonce, threshold);
    Py_END_ALLOW_THREADS

    PyObject *ret = Py_BuildValue("K", result);
    return ret;
}

static PyMethodDef work_methods[] = {
    {"do_work", work_do_work, METH_VARARGS, work_do_work_doc},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc,
"Function for calculating NANO proof-of-work");

static struct PyModuleDef
work_module = {
    PyModuleDef_HEAD_INIT,
    #ifdef WORK_REF
    "_work_ref",
    #elif WORK_SSE2
    "_work_sse2",
    #elif WORK_SSSE3
    "_work_ssse3",
    #elif WORK_SSE4_1
    "_work_sse4_1",
    #elif WORK_AVX
    "_work_avx",
    #elif WORK_NEON
    "_work_neon",
    #endif
    module_doc,
    -1,
    work_methods
};

#ifdef WORK_REF
PyMODINIT_FUNC PyInit__work_ref(void) {
    return PyModule_Create(&work_module);
}
#elif WORK_SSE2
PyMODINIT_FUNC PyInit__work_sse2(void) {
    return PyModule_Create(&work_module);
}
#elif WORK_SSSE3
PyMODINIT_FUNC PyInit__work_ssse3(void) {
    return PyModule_Create(&work_module);
}
#elif WORK_SSE4_1
PyMODINIT_FUNC PyInit__work_sse4_1(void) {
    return PyModule_Create(&work_module);
}
#elif WORK_AVX
PyMODINIT_FUNC PyInit__work_avx(void) {
    return PyModule_Create(&work_module);
}
#elif WORK_NEON
PyMODINIT_FUNC PyInit__work_neon(void) {
    return PyModule_Create(&work_module);
}
#endif
