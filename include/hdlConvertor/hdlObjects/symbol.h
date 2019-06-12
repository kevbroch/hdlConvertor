#pragma once

#include <vector>
#include <hdlConvertor/hdlObjects/bigInteger.h>
#include <hdlConvertor/hdlObjects/symbolType.h>
#include <hdlConvertor/hdlObjects/exprItem.h>

namespace hdlConvertor {
namespace hdlObjects {

class Expr;
class Symbol: public virtual ExprItem {
public:
	SymbolType type;
	int bits;
	LiteralVal value;
	const std::vector<Expr*> * value_arr;

	Symbol(const Symbol & s);
	Symbol(SymbolType type, LiteralVal value);
	Symbol(BigInteger value, int bits);
	Symbol(const std::vector<Expr*> * arr);

	ExprItem * clone() const;

	~Symbol();
};

}
}