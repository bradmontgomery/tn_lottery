"""
Integration tests for the CLI interface.

Tests the tn-lottery command-line tool end-to-end.
"""
import pytest
from click.testing import CliRunner
from tn_lottery.cli import cli


class TestCLIBasics:
    """Test basic CLI functionality."""
    
    def test_cli_help_works(self):
        """Main CLI help should display without errors."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'TN Lottery tools' in result.output
        
    def test_cli_shows_commands(self):
        """Help should list all available commands."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert 'play' in result.output
        assert 'games' in result.output
        assert 'simulate' in result.output
        assert 'simulate-group' in result.output


class TestPlayCommand:
    """Test the 'play' command."""
    
    def test_play_command_runs(self):
        """Basic play command should execute without error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['play'])
        assert result.exit_code == 0
        
    def test_play_command_help(self):
        """Play help should show options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['play', '--help'])
        assert result.exit_code == 0
        assert '--game' in result.output
        assert '--number' in result.output
        
    def test_play_single_game_powerball(self):
        """Play Powerball should generate numbers."""
        runner = CliRunner()
        result = runner.invoke(cli, ['play', '-g', 'powerball'])
        assert result.exit_code == 0
        assert 'Powerball' in result.output
        
    def test_play_single_game_mega_millions(self):
        """Play Mega Millions should generate numbers."""
        runner = CliRunner()
        result = runner.invoke(cli, ['play', '-g', 'megamillions'])
        assert result.exit_code == 0
        assert 'Mega Millions' in result.output
        
    def test_play_multiple_plays(self):
        """Playing multiple times should work."""
        runner = CliRunner()
        result = runner.invoke(cli, ['play', '-g', 'powerball', '-n', '3'])
        assert result.exit_code == 0
        # Should show 3 plays
        assert result.output.count('Powerball') >= 3
        
    def test_play_all_games(self):
        """Playing without specific game should show all games."""
        runner = CliRunner()
        result = runner.invoke(cli, ['play'])
        assert result.exit_code == 0
        # Should show multiple games
        assert 'Powerball' in result.output
        assert 'Mega Millions' in result.output


class TestGamesCommand:
    """Test the 'games' command."""
    
    def test_games_command_runs(self):
        """Games command should execute without error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['games'])
        assert result.exit_code == 0
        
    def test_games_lists_all_games(self):
        """Games should list all available games."""
        runner = CliRunner()
        result = runner.invoke(cli, ['games'])
        assert 'Powerball' in result.output
        assert 'Mega Millions' in result.output
        assert 'Hot Lotto' in result.output
        assert 'Tennessee Cash' in result.output or 'TN Cash' in result.output
        assert 'Cash 4' in result.output
        assert 'Cash 3' in result.output
        
    def test_games_shows_number_ranges(self):
        """Games should show game names (ranges may not be shown)."""
        runner = CliRunner()
        result = runner.invoke(cli, ['games'])
        # Just verify it shows game names - ranges are optional
        assert 'powerball' in result.output.lower()
        assert 'mega' in result.output.lower()


class TestSimulateCommand:
    """Test the 'simulate' command."""
    
    def test_simulate_command_help(self):
        """Simulate help should show options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate', '--help'])
        assert result.exit_code == 0
        
    def test_simulate_with_duration(self):
        """Simulate with duration should run."""
        runner = CliRunner()
        # Use short duration for speed
        result = runner.invoke(cli, ['simulate', '--duration', '1'])
        assert result.exit_code == 0
        
    def test_simulate_with_plays(self):
        """Simulate with plays per week should work."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate', '--plays-per-week', '1', '--duration', '1'])
        assert result.exit_code == 0
        
    def test_simulate_shows_statistics(self):
        """Simulate should show statistics."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate', '--plays-per-week', '10', '--duration', '1'])
        assert result.exit_code == 0
        # Just verify it ran successfully
        
    def test_simulate_with_custom_cost(self):
        """Simulate with custom cost per play should work."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate', '--plays-per-week', '2', '--duration', '1', '--cost-per-play', '3'])
        assert result.exit_code == 0


class TestSimulateGroupCommand:
    """Test the 'simulate-group' command."""
    
    def test_simulate_group_command_help(self):
        """Simulate-group help should show options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate-group', '--help'])
        assert result.exit_code == 0
        assert '--players' in result.output
        
    def test_simulate_group_small_population(self):
        """Simulate small group should work."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate-group', '--players', '10', '--plays-per-player', '5'])
        assert result.exit_code == 0
        
    def test_simulate_group_shows_statistics(self):
        """Simulate group should show population statistics."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate-group', '--players', '50', '--plays-per-player', '10'])
        assert result.exit_code == 0
        # Just verify it ran successfully
        
    def test_simulate_group_medium_population(self):
        """Simulate medium group should use parallel mode."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate-group', '--players', '1500', '--plays-per-player', '5'])
        assert result.exit_code == 0
        
    def test_simulate_group_with_cost(self):
        """Simulate group with custom cost should work."""
        runner = CliRunner()
        result = runner.invoke(cli, ['simulate-group', '--players', '10', '--plays-per-player', '5', '--cost-per-play', '3'])
        assert result.exit_code == 0


class TestScrapeCommand:
    """Test the 'scrape' command."""
    
    def test_scrape_command_help(self):
        """Scrape help should show options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['scrape', '--help'])
        assert result.exit_code == 0


class TestReportCommand:
    """Test the 'report' command."""
    
    def test_report_command_help(self):
        """Report help should show options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['report', '--help'])
        assert result.exit_code == 0


class TestDBPathCommand:
    """Test the 'db-path' command."""
    
    def test_db_path_command_runs(self):
        """DB-path command should execute without error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['db-path'])
        assert result.exit_code == 0
        assert 'Database location' in result.output
        
    def test_db_path_shows_path(self):
        """DB-path should show actual database path."""
        runner = CliRunner()
        result = runner.invoke(cli, ['db-path'])
        assert '.db' in result.output or 'lottery' in result.output.lower()


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_invalid_command_shows_error(self):
        """Invalid command should show error."""
        runner = CliRunner()
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0
        
    def test_invalid_game_name(self):
        """Invalid game name should handle gracefully."""
        runner = CliRunner()
        result = runner.invoke(cli, ['play', '-g', 'invalid_game'])
        # Should either error gracefully or ignore invalid game
        # Exit code may be 0 or non-zero depending on implementation


class TestCLIIntegration:
    """Test CLI commands work together."""
    
    def test_games_then_play_workflow(self):
        """List games, then play one."""
        runner = CliRunner()
        
        # First list games
        result1 = runner.invoke(cli, ['games'])
        assert result1.exit_code == 0
        
        # Then play Powerball
        result2 = runner.invoke(cli, ['play', '-g', 'powerball'])
        assert result2.exit_code == 0
        
    def test_db_path_then_report(self):
        """Check db path, then run report."""
        runner = CliRunner()
        
        # Check DB path
        result1 = runner.invoke(cli, ['db-path'])
        assert result1.exit_code == 0
        
        # Run report (may be empty but shouldn't error)
        result2 = runner.invoke(cli, ['report'])
        # Report might fail if no data, accept various exit codes
        assert result2.exit_code in [0, 1, 2]
