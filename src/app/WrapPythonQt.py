import os
import re
import sys
import argparse

def wrap(args):


    inFileNames = args.input_file
    outFileName = args.output_file
    exportSymbol = args.export_symbol
    exportHeader = args.export_header
    decoratorClassName = args.class_name
    classNamePrefixes = args.class_prefixes
    qtClassNamePrefixes = args.qt_class_prefixes
    moduleName = args.module_name
    autoClassIncludes = args.auto_class_includes

    if not decoratorClassName:
        if not outFileName.endswith('.h'):
            raise Exception('Error: when output class name is not provided then the'
                            ' output file extension must be .h')
        decoratorClassName = os.path.basename(outFileName).replace('.h', '')

    lines = []
    for inFileName in inFileNames:
        inFile = open(inFileName, 'r')
        lines += inFile.read().splitlines()
        inFile.close()

    classNameRegexes = [re.compile('\\b%s[a-zA-Z0-9]*' % prefix) for prefix in classNamePrefixes]
    qtClassNamePrefixes = tuple(qtClassNamePrefixes)
    moduleName = moduleName or 'PythonQt'
    exportInclude = '#include "%s"' % exportHeader if exportHeader else ''

    generatedCode = str()
    rePattern = re.compile('(?:(.+)\s+)?(\S+)::(\S+)\((.*)\).*')

    includeClasses = set()
    includeLines = list()

    for line in lines:


        if line.startswith("//"):
            generatedCode += "  " + line + "\n"
            continue
        elif line.startswith("#include"):
            includeLines.append(line)
            continue
        elif not line.strip():
            generatedCode += "\n"
            continue

        matchList = rePattern.findall(line)
        if not matchList or len(matchList[0]) != 4:
            raise Exception('Failed to match: "%s"' % line)

        matchList = list(matchList[0])
        return_type = matchList[0].strip()
        class_name = matchList[1]
        method_name = matchList[2]
        args = matchList[3]
        arg_list = args.split(",") if args.strip() else []

        is_static = return_type.startswith("static ")
        is_destructor = '~' == method_name[0]
        is_constructor = not is_destructor and return_type == ''
        if is_static:
            return_type = return_type[7:]
            decorator_method_name = "static_%s_%s" % (class_name, method_name)
        elif is_destructor:
            return_type = 'void'
            decorator_method_name = "delete_%s" % class_name
        elif is_constructor:
            return_type = '%s*' % class_name
            decorator_method_name = "new_%s" % class_name
        else:
            decorator_method_name = method_name

        includeClasses.add(class_name)

        for regex in classNameRegexes:
            classname_matches = regex.findall(return_type)
            for classname in classname_matches:
                includeClasses.add(classname)

        wrap_args = []
        if not is_static and not is_constructor:
            wrap_args.append("%s* inst" % class_name)

        wrap_args_call = []
        for i, arg_type in enumerate(arg_list):
            arg_name = "arg%d" % i
            wrap_args.append("%s %s" % (arg_type.strip(), arg_name))
            wrap_args_call.append(arg_name)

        callStatement = "%s(%s)" % (method_name, ", ".join(wrap_args_call))
        if is_static:
            callStatement = "%s::%s" % (class_name, callStatement)
        elif is_destructor:
            callStatement = 'delete inst'
        elif is_constructor:
            callStatement = 'new %s' % callStatement
        else:
            callStatement = "inst->%s" % callStatement

        if return_type == 'void':
            returnStatement = "%s;" % callStatement
        else:
            returnStatement = "return %s;" % callStatement


        outStr = \
'''
  %s %s(%s)
    {
    %s
    }
'''
        outStr = outStr % (return_type,
                           decorator_method_name,
                           ", ".join(wrap_args),
                           returnStatement)

        generatedCode += outStr


    sortedClasses = list(includeClasses)
    sortedClasses.sort()
    if autoClassIncludes:
        includeLines += ['#include "%s.h"' % className for className in sortedClasses]

    classIncludes = "\n".join(includeLines)
    classRegisters = "\n".join(['    this->registerClassForPythonQt(&%s::staticMetaObject);' % className
                                for className in sortedClasses if className.startswith(qtClassNamePrefixes)])

    outFile = open(outFileName, 'w')
    outFile.write('''
#ifndef __%s_h
#define __%s_h

#include <QObject>
#include <PythonQt.h>

%s
%s

class %s %s : public QObject
{
  Q_OBJECT

public:

  %s(QObject* parent=0) : QObject(parent)
    {
%s
    }

  inline void registerClassForPythonQt(const QMetaObject* metaobject)
    {
    PythonQt::self()->registerClass(metaobject, "%s");
    }

public Q_SLOTS:

%s

};

#endif''' % (
        decoratorClassName,
        decoratorClassName,
        exportInclude,
        classIncludes,
        exportSymbol,
        decoratorClassName,
        decoratorClassName,
        classRegisters,
        moduleName,
        generatedCode))

    outFile.close()


def main():

    parser = argparse.ArgumentParser(description='Generate a PythonQt decorator class file from a list of method signatures.')
    parser.add_argument('--input-file', '-i', nargs='+', required=True, help='A text file with method signatures, one per line.')
    parser.add_argument('--output-file', '-o', required=True, help='The output filename.  The file extension should be .h')
    parser.add_argument('--module-name', default='', help='The Python module name under which Qt classes will be registered.')
    parser.add_argument('--class-name', default='', help='The C++ class name of the generated decorator.'
                                                         ' If empty, it will be computed from the output filename.')
    parser.add_argument('--export-symbol', default='', help='An export symbol that will be added to the class declaration.')
    parser.add_argument('--export-header', default='', help='A header filename that defines an export symbol.')
    parser.add_argument('--class-prefixes', nargs='*', help='A list of class name prefixes.')
    parser.add_argument('--qt-class-prefixes', nargs='*', help='A list of Qt class name prefixes.')
    parser.add_argument('--auto-class-includes', action='store_true', help='Automatically generate include statements from class names.')

    args = parser.parse_args()

    wrap(args)

if __name__ == '__main__':
    main()
