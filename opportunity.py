# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Bool, Eval
from trytond.transaction import Transaction

__all__ = ['Relation', 'PartyCampaign', 'CreateCampaignStart',
    'CreateCampaign']
__metaclass__ = PoolMeta


class Relation:
    __name__ = 'party.relation.type'
    available_on_campaign = fields.Function(fields.Boolean('Available on '
            'campaing'), 'get_available_on_campaign',
        searcher='search_available_on_campaign')

    @classmethod
    def get_available_on_campaign(cls, relations, name):
        pool = Pool()
        Config = pool.get('sale.configuration')
        config = Config(1)

        res = {}.fromkeys(relations, False)
        for relation in config.relations:
            if relation.id in res:
                res[relation.id] = True
        return res

    @classmethod
    def search_available_on_campaign(cls, name, clause):
        pool = Pool()
        Config = pool.get('sale.configuration')
        config = Config(1)
        conversion = {
            '=': 'in',
            '!=': 'not in',
            }

        allowed = [r.id for r in config.relation_types]
        if not allowed or not clause[1] in conversion:
            return [('id', '=', -1)]

        operator = conversion[clause[1]]
        reverse = {
            'in': 'not in',
            'not in': 'in',
            }
        if clause[2]:
            return [('id', operator, allowed)]
        else:
            return [('id', reverse[operator], allowed)]


class PartyCampaign:
    __name__ = 'sale.opportunity.campaign-party.party'

    def _get_opportunities(self):
        opportunities = super(PartyCampaign, self)._get_opportunities()
        relation = Transaction().context.get('relation')
        if relation:
            new_opportunities = []
            for relation in self.party.relations:
                if relation.type.id == relation:
                    for opportunity in opportunities:
                        new_opportunity = opportunity.copy()
                        new_opportunity['contact'] = relation.to.id
                        new_opportunities.append(new_opportunity)
                    if not self.start.all_contacts:
                        break
            if new_opportunities:
                return new_opportunities
        return opportunities


class PartyCampaign:
    __name__ = 'sale.opportunity.campaign-party.party'

    def _get_opportunities(self):
        opportunities = super(PartyCampaign, self)._get_opportunities()
        relation = Transaction().context.get('relation')
        if relation:
            new_opportunities = []
            for relation in self.party.relations:
                if relation.type.id == relation:
                    for opportunity in opportunities:
                        new_opportunity = opportunity.copy()
                        new_opportunity['contact'] = relation.to.id
                        new_opportunities.append(new_opportunity)
                    if not self.start.all_contacts:
                        break
            if new_opportunities:
                return new_opportunities
        return opportunities


class CreateCampaignStart:
    __name__ = 'sale.opportunity.create_campaign.start'
    relation_visible = fields.Boolean('Relation Visible')
    relation = fields.Many2One('party.relation.type', 'Relation',
        domain=[
            ('available_on_campaign', '=', True),
            ],
        states={
            'invisible': ~Bool(Eval('relation_visible', False)),
            },
        depends=['relation_visible'])
    all_contacts = fields.Boolean('All Contacts',
        states={
            'invisible': ~Bool(Eval('relation', 0))
            },
        depends=['relation'],
        help='If marked a lead will be created for each contact of the '
        'selected type. Otherwise only the first one will be used.')


class CreateCampaign:
    __name__ = 'sale.opportunity.create_campaign'

    def default_start(self, fields):
        pool = Pool()
        Config = pool.get('sale.configuration')
        config = Config(1)
        return {'relation_visible': bool(config.relation_types)}

    def do_leads(self, action):
        context = {}
        if self.start.relation:
            context['relation'] = self.start.relation.id
        with Transaction().set_context(context):
            return super(CreateCampaign, self).do_leads(action)
