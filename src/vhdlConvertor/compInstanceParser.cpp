#include <hdlConvertor/notImplementedLogger.h>
#include <hdlConvertor/vhdlConvertor/compInstanceParser.h>
#include <hdlConvertor/vhdlConvertor/exprParser.h>
#include <hdlConvertor/vhdlConvertor/literalParser.h>
#include <hdlConvertor/vhdlConvertor/referenceParser.h>

namespace hdlConvertor {
namespace vhdl {

using vhdlParser = vhdl_antlr::vhdlParser;
using namespace hdlConvertor::hdlObjects;

std::unique_ptr<HdlCompInstance> VhdlCompInstanceParser::visitComponent_instantiation_statement(
		vhdlParser::Component_instantiation_statementContext *ctx,
		const std::string &name) {
	// component_instantiation_statement:
	//       instantiated_unit
	//           ( generic_map_aspect )?
	//           ( port_map_aspect )? SEMI
	// ;
	auto ci = visitInstantiated_unit(ctx->instantiated_unit());
	ci->name = iHdlExpr::ID(name);
	ci->position.update_from_elem(ctx);

	auto gma = ctx->generic_map_aspect();
	if (gma) {
		auto gmas = visitGeneric_map_aspect(gma);
		for (auto & gm : *gmas) {
			ci->genericMap.push_back(move(gm));
		}
	}
	auto pma = ctx->port_map_aspect();
	if (pma) {
		auto pmas = visitPort_map_aspect(pma);
		for (auto & pm : *pmas) {
			ci->portMap.push_back(move(pm));
		}
	}
	return ci;
}

std::unique_ptr<HdlCompInstance> VhdlCompInstanceParser::visitInstantiated_unit(
		vhdlParser::Instantiated_unitContext *ctx) {
	// instantiated_unit
	// : ( COMPONENT )? name
	// | ENTITY name ( LPAREN identifier RPAREN )?
	// | CONFIGURATION name
	// ;

	auto _id = ctx->identifier();
	if (_id) {
		NotImplementedLogger::print(
				"CompInstanceParser.visitInstantiated_unit - Identifier", _id);
	}
	auto ent_name = VhdlReferenceParser::visitName(ctx->name());
	return std::make_unique<HdlCompInstance>(nullptr, std::move(ent_name));
}

std::unique_ptr<std::vector<std::unique_ptr<iHdlExpr>>> VhdlCompInstanceParser::visitGeneric_map_aspect(
		vhdlParser::Generic_map_aspectContext *ctx) {
	//generic_map_aspect
	//  : GENERIC MAP LPAREN association_list RPAREN
	//  ;
	return VhdlExprParser::visitAssociation_list(ctx->association_list());
}

std::unique_ptr<std::vector<std::unique_ptr<iHdlExpr>>> VhdlCompInstanceParser::visitPort_map_aspect(
		vhdlParser::Port_map_aspectContext *ctx) {
	//port_map_aspect
	//  : PORT MAP LPAREN association_list RPAREN
	//  ;
	return VhdlExprParser::visitAssociation_list(ctx->association_list());
}

}
}
