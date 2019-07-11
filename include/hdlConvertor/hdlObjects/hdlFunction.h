#pragma once
#include <vector>
#include <hdlConvertor/hdlObjects/named.h>
#include <hdlConvertor/hdlObjects/iHdlExpr.h>
#include <hdlConvertor/hdlObjects/iHdlStatement.h>
#include <hdlConvertor/hdlObjects/iHdlObj.h>
#include <hdlConvertor/hdlObjects/hdlVariableDef.h>

namespace hdlConvertor {
namespace hdlObjects {

class HdlFunction: public WithNameAndDoc, public iHdlObj {
public:
	const iHdlExpr * returnT;
	const std::vector<HdlVariableDef*> * params;
	std::vector<HdlVariableDef*> locals;
	std::vector<iHdlStatement*> body;
	const bool is_operator;
	bool declaration_only;

	HdlFunction(const std::string & name, bool is_operator, iHdlExpr * returnT,
			std::vector<HdlVariableDef*> * params);
	~HdlFunction();
};

}
}
