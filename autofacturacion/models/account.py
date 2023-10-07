
            try:
                moves.action_process_edi_web_services()
                _logger.warning("timbrando")
                _logger.warning(moves)
                moves.action_retry_edi_documents_error()
                # _logger.warning(moves.l10n_mx_edi_payment_method_id)
                # _logger.warning(moves.l10n_mx_edi_payment_policy)
                if(moves.edi_error_count == 1):
                    _logger.warning("error")
                    raise ValidationError(_(moves.edi_error_message))
                    return
                else:
                    _logger.warning(moves.edi_document_ids)
                    for x in moves.edi_document_ids:
                        _logger.warning(x.name)
                        if(x.edi_format_name == 'CFDI (4.0)'):
                            return {
                                'type': 'ir.actions.act_url',
                                'url': '/autofacturador/xml_report/%s' % (x.id),
                                'target': 'self',
                            }
            except ValidationError as exc:
                raise ValidationError(_(exc))
            except UserError as excUser:
                raise UserError(_(excUser))
                _logger.warning("CREA INVOICE")

if(not moves.edi_state == 'sent'):
                try:
                    moves.action_process_edi_web_services()
                    # moves.action_retry_edi_documents_error()
                    # if(moves.edi_error_count == 1):
                    #     raise ValidationError(_(moves.edi_error_message))
                    # else:
                    #     for x in moves.edi_document_ids:
                    #         if(x.edi_format_name == 'CFDI (4.0)'):
                    #             return {
                    #                 'type': 'ir.actions.act_url',
                    #                 'url': '/autofacturador/xml_report/%s' % (x.id),
                    #                 'target': 'self',
                    #             }
                    _logger.warning('timbrar')
                except ValidationError as exc:
                    raise ValidationError(_(exc))
                except UserError as excUser:
                    raise UserError(_(excUser))
        