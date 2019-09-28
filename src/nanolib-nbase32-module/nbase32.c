#define PY_SSIZE_T_CLEAN 1
#include "Python.h"

#include <stdint.h>
#include <stdio.h>

#include "bit_array.h"

#define NBASE32_CHAR_BITS 5
#define NBase32ToBytesLen(size) ((size*5) / 8)
#define BytesToNBase32Len(size) (((size*8) + 5 - 1) / 5)

static const uint8_t NBASE32_TABLE[256] =
{
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 1, 2, 3, 4, 5,
    6, 7, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 8, 9, 10, 11, 12, 13, 14,
    15, 16, 17, 18, 0, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 0, 28,
    29, 30, 31, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

static const char NBASE32_VALID_TABLE[256] = "0000000000000000000000000000000000000000000000000101111111000000000000000000000000000000000000000111111111110111111111011110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
static const char NBASE32_CHARS[32] = "13456789abcdefghijkmnopqrstuwxyz";

int nbase32_to_bytes(const uint8_t *nbase32, const ssize_t nbase32_size, uint8_t *result) {
    uint64_t bitarr_bits = nbase32_size * 5;

    BIT_ARRAY *bitarr = bit_array_create(bitarr_bits);

    for (uint64_t i=0; i < bitarr_bits; i += NBASE32_CHAR_BITS) {
        uint8_t byte = nbase32[(i / NBASE32_CHAR_BITS)];
        if (NBASE32_VALID_TABLE[byte] == 48) {
            bit_array_free(bitarr);
            return 1;
        }
        uint8_t value = NBASE32_TABLE[byte];
        bit_array_assign(bitarr, i, (value >> 4) & 1);
        bit_array_assign(bitarr, i+1, (value >> 3) & 1);
        bit_array_assign(bitarr, i+2, (value >> 2) & 1);
        bit_array_assign(bitarr, i+3, (value >> 1) & 1);
        bit_array_assign(bitarr, i+4, (value >> 0) & 1);
    }

    uint8_t leftover = bitarr_bits % 8;

    for (uint64_t i=leftover; i < bitarr_bits; i += 8) {
        uint64_t byte_index = i / 8;

        result[byte_index] = (uint8_t)(
            (bit_array_get(bitarr, i) << 7) +
            (bit_array_get(bitarr, i+1) << 6) +
            (bit_array_get(bitarr, i+2) << 5) +
            (bit_array_get(bitarr, i+3) << 4) +
            (bit_array_get(bitarr, i+4) << 3) +
            (bit_array_get(bitarr, i+5) << 2) +
            (bit_array_get(bitarr, i+6) << 1) +
            (bit_array_get(bitarr, i+7) << 0)
        );
    }

    bit_array_free(bitarr);

    return 0;
};

void bytes_to_nbase32(const uint8_t *bytes, const ssize_t bytes_size, uint8_t *result) {
    uint64_t bitarr_bits = bytes_size * 8;
    uint8_t leftover = 5 - (bitarr_bits % 5);
    bitarr_bits += leftover;

    BIT_ARRAY *bitarr = bit_array_create(bitarr_bits);

    for (uint64_t i=leftover; i < bitarr_bits; i += 8) {
        uint32_t b_i = (i - leftover) / 8;
        uint8_t value = bytes[b_i];
        bit_array_assign(bitarr, i, (value >> 7) & 1);
        bit_array_assign(bitarr, i+1, (value >> 6) & 1);
        bit_array_assign(bitarr, i+2, (value >> 5) & 1);
        bit_array_assign(bitarr, i+3, (value >> 4) & 1);
        bit_array_assign(bitarr, i+4, (value >> 3) & 1);
        bit_array_assign(bitarr, i+5, (value >> 2) & 1);
        bit_array_assign(bitarr, i+6, (value >> 1) & 1);
        bit_array_assign(bitarr, i+7, (value >> 0) & 1);
    }

    for (uint64_t i=0; i < bitarr_bits; i += 5) {
        uint64_t byte_index = i / 5;
        result[byte_index] = (uint8_t)(
            (bit_array_get(bitarr, i) << 4) +
            (bit_array_get(bitarr, i+1) << 3) +
            (bit_array_get(bitarr, i+2) << 2) +
            (bit_array_get(bitarr, i+3) << 1) +
            (bit_array_get(bitarr, i+4) << 0)
        );
    }

    bit_array_free(bitarr);

    uint32_t result_size = BytesToNBase32Len(bytes_size);

    uint8_t start = result_size % 8 == 0 ? 1 : 0;

    for (uint64_t i=start; i < result_size + start; i++) {
        result[i-start] = NBASE32_CHARS[result[i]];
    }
}

PyDoc_STRVAR(nbase32_nbase32_to_bytes_doc,
"nbase32_to_bytes(nbase32)\n\
\n\
Convert NANO BASE32 encoded string to bytes.");

static PyObject *
nbase32_nbase32_to_bytes(PyObject *self, PyObject *args)
{
    const uint8_t *nbase32;
    Py_ssize_t nbase32_size;

    if (!PyArg_ParseTuple(args, "y#", &nbase32, &nbase32_size)) {
        return NULL;
    }

    if (nbase32_size == 0) {
        PyErr_SetString(PyExc_ValueError,
                        "String is empty");
        return NULL;
    }

    if (nbase32_size > UINT32_MAX) {
        PyErr_SetString(PyExc_ValueError,
                        "String longer than (2**32)-1 bytes");
        return NULL;
    }

    uint32_t result_size = NBase32ToBytesLen(nbase32_size);
    uint8_t *result = malloc(sizeof(uint8_t)*result_size);
    int error = nbase32_to_bytes(nbase32, nbase32_size, result);

    if (error) {
        PyErr_SetString(PyExc_ValueError,
                        "String is not Nano Base32-encoded");
        free(result);
        return NULL;
    }

    PyObject *ret = Py_BuildValue("y#", result, result_size);
    return ret;
};

PyDoc_STRVAR(nbase32_bytes_to_nbase32_doc,
"bytes_to_nbase32(b)\n\
\n\
Convert bytes to NANO BASE32 encoded string");

static PyObject *
nbase32_bytes_to_nbase32(PyObject *self, PyObject *args)
{
    const uint8_t *bytes;
    Py_ssize_t bytes_size;

    if (!PyArg_ParseTuple(args, "y#", &bytes, &bytes_size)) {
        return NULL;
    }

    if (bytes_size == 0) {
        PyErr_SetString(PyExc_ValueError,
                        "Byte array is empty");
        return NULL;
    }

    uint64_t result_size = BytesToNBase32Len(bytes_size);

    if (result_size > UINT32_MAX) {
        PyErr_SetString(PyExc_ValueError,
                        "Resulting Base32 string longer than (2**32)-1 bytes");
        return NULL;
    }

    uint8_t *result = malloc(sizeof(uint8_t)*result_size);
    bytes_to_nbase32(bytes, bytes_size, result);

    PyObject *ret = Py_BuildValue("y#", result, result_size);
    return ret;
}

static PyMethodDef nbase32_methods[] = {
    {"nbase32_to_bytes", nbase32_nbase32_to_bytes, METH_VARARGS, nbase32_nbase32_to_bytes_doc},
    {"bytes_to_nbase32", nbase32_bytes_to_nbase32, METH_VARARGS, nbase32_bytes_to_nbase32_doc},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc,
"Functions for NANO BASE32 conversions");

static struct PyModuleDef
nbase32_module = {
    PyModuleDef_HEAD_INIT,
    "_nbase32",
    module_doc,
    -1,
    nbase32_methods
};

PyMODINIT_FUNC PyInit__nbase32(void) {
    return PyModule_Create(&nbase32_module);
}
