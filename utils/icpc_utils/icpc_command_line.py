import click

from aox.command_line.command import cli as aox_cli
from aox.settings import settings_proxy
from .icpc_controller import IcpcController


__all__ = ['icpc_cli']


def create_icpc_cli():
    controller = IcpcController()

    @aox_cli.group(
        invoke_without_command=True,
        help=(
            "A utility tool to manage your code, and display a summary of your "
            "stars, for your ICPC submissions\n"
        ),
        short_help="Manage code for ICPC submissions",
    )
    @click.pass_context
    def icpc(ctx):
        settings_proxy.ensure_default()
        if ctx.invoked_subcommand:
            return
        controller.list_years()

    @icpc.group(
        invoke_without_command=True,
        help=(
            "Create, test & run a particular challenge, or do other operations "
            "on it"
        ),
        short_help="Create and Test & run a challenge",
    )
    @click.argument('year', type=int)
    @click.argument('part', type=str)
    @click.option('-p', '--path', 'path', type=str)
    @click.option('-f', '--force', 'force', is_flag=True)
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.option('--debug-interval', '-i', 'debug_interval', type=float,
                  default=5)
    @click.pass_context
    def challenge(ctx, year, part, path, force, filters_texts, debug,
                  debug_interval):
        if path is not None:
            year, part = settings_proxy().challenges_boilerplate\
                .extract_icpc_from_filename(path)
            ctx.params['year'], ctx.params['part'] = year, part
        if ctx.invoked_subcommand:
            return
        controller.test_and_run_challenge(
            year, part, force, filters_texts, debug, debug_interval)

    @challenge.command(
        name="all",
        help=(
            "Test and run the challenge code"
        ),
        short_help="Test and run challenge",
    )
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.option('--debug-interval', '-i', 'debug_interval', type=float,
                  default=5)
    @click.pass_context
    def run_all(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.test_and_run_challenge(
            params['year'], params['part'], params['force'],
            params['filters_texts'], params['debug'], params['debug_interval'])

    @challenge.command(
        help=(
            "Test the challenge, based on doctests in the file"
        ),
        short_help="Run tests",
    )
    @click.option('--test', '-t', 'filters_texts', multiple=True)
    @click.pass_context
    def test(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.test_challenge(
            params['year'], params['part'], params['force'],
            params['filters_texts'])

    @challenge.command(
        help=(
            "Run the challenge and print the solution"
        ),
        short_help="Run the challenge",
    )
    @click.argument('input_names', type=str, nargs=-1)
    @click.option('--all', '-a', 'all_inputs', is_flag=True)
    @click.option('--cases', '-c', 'case_indexes', type=int, multiple=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.option('--debug-interval', '-i', 'debug_interval', type=float,
                  default=5)
    @click.pass_context
    def run(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.run_challenge_many(
            params['year'], params['part'],
            params['input_names'], params['all_inputs'], params['case_indexes'],
            params['force'], params['debug'], params['debug_interval'])

    @challenge.command(
        help=(
            "Run the challenge with a particular input and check it's output"
        ),
        short_help="Check the challenge",
    )
    @click.argument('input_names', type=str, nargs=-1)
    @click.option('--all', '-a', 'all_inputs', is_flag=True)
    @click.option('--cases', '-c', 'case_indexes', type=int, multiple=True)
    @click.option('--verbose', '-v', 'verbose', is_flag=True)
    @click.option('--very-verbose', '-vv', 'very_verbose', is_flag=True)
    @click.option('--debug', '-d', 'debug', is_flag=True)
    @click.option('--debug-interval', '-i', 'debug_interval', type=float,
                  default=5)
    @click.pass_context
    def check(ctx, **params):
        params = {
            **ctx.parent.params,
            **params,
        }
        controller.check_challenge_many(
            params['year'], params['part'], params['force'],
            params['input_names'], params['all_inputs'], params['case_indexes'], params['verbose'], params['very_verbose'],
            params['debug'], params['debug_interval'])

    @challenge.command(
        help=(
            "If the challenge offers an interactive play mode, run it. The "
            "challenge needs to have defined a `Challenge.play` method"
        ),
        short_help="Run interactive mode (if defined)",
    )
    @click.pass_context
    def play(ctx):
        params = ctx.parent.params
        controller.play_challenge(params['year'], params['part'], params['force'])

    return icpc


icpc_cli = create_icpc_cli()
